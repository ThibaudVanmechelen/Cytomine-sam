"""Prediction API"""

from typing import Dict, Any, List, Optional, Union

import geojson
import numpy as np

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Request

from cytomine import Cytomine
from cytomine.models import ImageInstance

from src.config import Settings, get_settings

from src.api.models.model import SegmentationRequest, SmartSegmentationRequest
from src.api.models.validate import validate_box_feature, validate_point_feature

from src.utils.convert_geojson import mask_to_geojson
from src.utils.window import load_cytomine_window_image
from src.utils.align_prompts import align_box_prompt, align_point_prompt
from src.utils.format_prompt import format_point_prompt, format_box_prompt
from src.utils.postprocess import post_process_segmentation_mask
from src.utils.extract_img import get_roi_around_annotation
from src.utils.annotations import fetch_included_annotations


router = APIRouter()


@router.post("/prediction")
async def predict(
        request: Request,
        segmentation_input: SegmentationRequest,
        settings: Settings = Depends(get_settings)
    ) -> JSONResponse:
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
        result = run_segmentation_pipeline(
            request = request,
            image_id = segmentation_input.image_id,
            geometry = segmentation_input.geometry,
            points = segmentation_input.points,
            settings = settings
        )

    except Exception as e:
        raise HTTPException(status_code = 400, detail = str(e)) from e

    if not result:
        return JSONResponse(status_code = 204, content = {"message": "No geometry found"})

    return JSONResponse(content = result)


@router.post("/smart_prediction")
async def smart_predict(
        request: Request,
        segmentation_input: SmartSegmentationRequest,
        settings: Settings = Depends(get_settings)
    ) -> JSONResponse:
    """
    Function to handle the segmentation request, but here the core does not need to provide 
    the point prompts, the point prompts are inferred from the point annotations of the user 
    that are located inside the geometry (Box), on the same WSI.

    Args:
        (request: Request): the HTTP request.
        (segmentation_input: SmartSegmentationRequest): the segmentation details.
        (settings: Settings): the settings.

    Returns:
        (JSONResponse): the JSON response containing the new GeoJSON annotation.
    """
    # Check prompt coordinates format
    try:
        validate_box_feature(segmentation_input.geometry)

        points = fetch_included_annotations(
            image_id = segmentation_input.image_id,
            user_id = segmentation_input.user_id,
            geometry = segmentation_input.geometry,
            settings = settings
        )

        result = run_segmentation_pipeline(
            request = request,
            image_id = segmentation_input.image_id,
            geometry = segmentation_input.geometry,
            points = points if points else None,
            settings = settings
        )

    except Exception as e:
        raise HTTPException(status_code = 400, detail = str(e)) from e

    if not result:
        return JSONResponse(status_code = 204, content = {"message": "No geometry found"})

    return JSONResponse(content = result)


def run_segmentation_pipeline(
        request: Request,
        image_id: int,
        geometry: Dict[str, Any],
        points: Optional[List[Dict[str, Any]]],
        settings: Settings
    ) -> Union[geojson.Feature, None]:
    """
    Function to run the segmentation model for the incoming request and its prompts.

    Args:
        (request: Request): the HTTP request.
        (image_id: int): the id of the image to segment.
        (geometry: Dict[str, Any]): the box geometry for this image.
        (points: Optional[List[Dict[str, Any]]]): the additional (optional) point prompts.
        (settings: Settings): the settings.

    Returns:
        (geojson.Feature, or None): Returns the structure as a GeoJSON.
    """
    validate_box_feature(geometry)

    points_data = points if points is not None else []
    for pt in points_data:
        validate_point_feature(pt)

    # Box has coordinates according to the entire image referential
    box_prompt = format_box_prompt(geometry)
    point_prompt, point_label = format_point_prompt(points_data) # same for the points

    # Extract corresponding part of the image
    with Cytomine(settings.keys['host'], settings.keys['public_key'],
                  settings.keys['private_key'], verbose = False):

        img = ImageInstance().fetch(image_id)
        img_height = img.height

        x, y, annot_width, annot_height = get_roi_around_annotation(img, box_prompt)

        cropped_img = load_cytomine_window_image(img, x, y, annot_width, annot_height)
        if cropped_img is None:
            raise HTTPException(status_code = 500, detail = "Failed to load image from Cytomine.")

    # Align prompt referential
    box_prompt = align_box_prompt(box_prompt, x, y, img_height)

    if point_prompt is not None:
        point_prompt = align_point_prompt(point_prompt, x, y, img_height)

    # Predict and post process
    predictor = request.app.state.predictor
    predictor.set_image(cropped_img)

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
    output_mask = post_process_segmentation_mask(best_mask)

    # Format output
    geojson_mask = mask_to_geojson(output_mask, img_height, x, y)

    return geojson_mask
