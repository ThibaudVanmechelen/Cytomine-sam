"""Prediction API"""
import json

from cytomine import Cytomine
from cytomine.models import ImageInstance

from models.model import *
from models.validate import *

from utils.extract_img import *
from utils.format_prompt import *
from utils.align_prompts import *
from utils.window import *
from utils.convert_geojson import mask_to_geojson
from utils.postprocess import post_process_segmentation_mask, upscale_mask

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    UploadFile,
    File,
    Form
)
from fastapi.responses import JSONResponse

from src.config import Settings, get_settings

router = APIRouter()

@router.post("/prediction/from_id") # TODO handle request as an argument
async def predict_from_id(req: SegmentationFromIdRequest,
                          settings: Settings = Depends(get_settings)): # only download a patch
    try:
        box_data = GeoJSONPolygon(**json.loads(req.geometry))

    except Exception as e:
        raise HTTPException(status_code = 400, detail = f"Invalid geometry: {e}")

    try:
        points_data = [GeoJsonPoint(**pt) for pt in json.loads(req.points)] if req.points else []

    except Exception as e:
        raise HTTPException(status_code = 400, detail = f"Invalid points format: {e}")

    # Check prompt coordinates format
    try:
        validate_box(box_data)
        
        for pt in points_data:
            validate_coordinates(pt)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code = 400, detail = str(e))
    
    box_global = format_box_prompt(box_data) # the box has coordinates according to the entire image referential

    # Extract corresponding part of the image
    with Cytomine(settings.keys['host'], settings.keys['public_key'], settings.keys['private_key'], verbose = False) as cytomine:
        img = ImageInstance().fetch(req.image_id)
        x, y, width, height = get_roi_around_annotation_for_instance(img, box_global)
        cropped_img = load_cytomine_window_image(img, x, y, width, height)
        resized_cropped_img, cropped_width, cropped_height = resize_to_max_size(cropped_img, MAX_SIZE)

    # Align prompt referential
    box_prompt = align_box_prompt(box_global, x, y, height)
    point_prompt, point_label = align_point_prompt(points_data, x, y, height)

    # Predict and post process
    predictor = req.request.app.state.predictor
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
    output_mask = upscale_mask(post_processed_mask, (cropped_height, cropped_width))

    # Format output
    geojson_mask = mask_to_geojson(output_mask, x, y)

    if not geojson_mask:
        return JSONResponse(status_code = 204, content = {"message": "No geometry found"})

    return JSONResponse(content = geojson_mask, content = {"message": "Mask found"})