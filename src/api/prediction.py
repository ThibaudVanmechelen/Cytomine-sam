"""Prediction API"""

from io import BytesIO
import matplotlib.pyplot as plt
from pathlib import Path
import json

from models.model import *
from models.validate import *
from utils.format_prompt import *
from utils.align_prompts import *
from utils.extract_img import extract_img_region
from utils.convert_geojson import mask_to_geojson
from utils.postprocess import post_process_segmentation_mask, upscale_mask

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    UploadFile,
    File,
    Form
)
from fastapi.responses import JSONResponse

from src.config import Settings, get_settings

router = APIRouter()

@router.post("/prediction/upload")
async def predict_from_upload(
    request: Request,
    image: UploadFile = File(...),
    geometry: str = Form(...),
    points: Optional[str] = Form(None),
):
    # Check types
    try:
        box_data = GeoJSONPolygon(**json.loads(geometry))

    except Exception as e:
        raise HTTPException(status_code = 400, detail = f"Invalid geometry: {e}")

    try:
        points_data = [GeoJsonPoint(**pt) for pt in json.loads(points)] if points else []

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
    contents = await image.read()
    try:
        img = plt.imread(BytesIO(contents))
        if img.dtype == np.float32 or img.dtype == np.float64:
            img = (img * 255).astype(np.uint8) # shape: HxWxC

        img_height = img.shape[0]

    except Exception as e:
        raise HTTPException(status_code = 400, detail = f"Image read error: {e}")
    
    try:
        formatted_image, x_tl, y_tl, cropped_width, cropped_height = extract_img_region(img, box_global)

    except Exception as e:
        raise HTTPException(status_code = 400, detail = f"Image formatting error: {e}")

    # Align prompt referential
    box_prompt = align_box_prompt(box_global, x_tl, y_tl, img_height)
    point_prompt, point_label = align_point_prompt(points_data, x_tl, y_tl, img_height)

    # Predict and post process
    predictor = request.app.state.predictor
    predictor.set_image(formatted_image)

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
    geojson_mask = mask_to_geojson(output_mask, x_tl, y_tl)

    if not geojson_mask:
        return JSONResponse(status_code = 204, content = {"message": "No geometry found"})

    return JSONResponse(content = geojson_mask, content = {"message": "Mask found"})

@router.post("/prediction/from_id")
async def predict_from_id():
    return
