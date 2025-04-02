"""Prediction API"""
import numpy as np

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Request

from cytomine import Cytomine
from cytomine.models import ImageInstance

from src.config import Settings, get_settings

from models.model import SegmentationRequest
from models.validate import validate_box_feature, validate_point_feature

from utils.convert_geojson import mask_to_geojson
from utils.window import load_cytomine_window_image
from utils.align_prompts import align_box_prompt, align_point_prompt
from utils.format_prompt import format_point_prompt, format_box_prompt
from utils.postprocess import post_process_segmentation_mask, upscale_mask
from utils.extract_img import get_roi_around_annotation, resize_to_max_size


router = APIRouter()


@router.post("/prediction")
async def predict(
        request: Request,
        segmentation_input: SegmentationRequest,
        settings: Settings = Depends(get_settings)
    ):
    """
    Function to handle the segmentation request.

    Args:
        (request: Request): the HTTP request.
        (segmentation_input: SegmentationRequest): the segmentation details.
        (settings: Settings): the settings.

    Returns:
        (JSONResponse): the JSON response containing the new GeoJSON annotation.
    """
    # Check prompt coordinates format
    try:
        validate_box_feature(segmentation_input.geometry)
        
        points_data = segmentation_input.points if segmentation_input.points is not None else []
        for pt in points_data:
            validate_point_feature(pt)

        box_prompt = format_box_prompt(segmentation_input.geometry) # the box has coordinates according to the entire image referential
        point_prompt, point_label = format_point_prompt(points_data) # same for the points

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code = 400, detail = str(e))

    # Extract corresponding part of the image
    with Cytomine(settings.keys['host'], settings.keys['public_key'], settings.keys['private_key'], verbose = False) as cytomine:
        img = ImageInstance().fetch(segmentation_input.image_id)
        x, y, annot_width, annot_height = get_roi_around_annotation(img, box_prompt)
        cropped_img = load_cytomine_window_image(img, x, y, annot_width, annot_height)
        resized_cropped_img, original_dimw, original_dimh = resize_to_max_size(cropped_img)

    # Align prompt referential
    box_prompt = align_box_prompt(box_prompt, x, y, original_dimh)
    point_prompt = align_point_prompt(point_prompt, x, y, original_dimh)

    # Predict and post process
    predictor = request.app.state.predictor
    predictor.set_image(resized_cropped_img)

    masks, ious, _ = predictor.predict(
        point_coords = point_prompt,
        point_labels = point_label,
        box = box_prompt,
        mask_input = None,
        multimask_output = True,
        return_logits = False,
        normalize_coords = True,
    )

    best_mask = masks[np.argmax(ious)] # shape: H x W
    post_processed_mask = post_process_segmentation_mask(best_mask)

    # Resize the output if needed
    output_mask = upscale_mask(post_processed_mask, (original_dimh, original_dimw))

    # Format output
    geojson_mask = mask_to_geojson(output_mask, original_dimh, x, y)

    if not geojson_mask:
        return JSONResponse(status_code = 204, content = {"message": "No geometry found"})

    return JSONResponse(content = geojson_mask)