# backend/topview/router.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import numpy as np
import cv2
import io

from .model import TopViewModel

router = APIRouter(prefix="/topview", tags=["Top-View Tree Detection"])

# initialize model (loading happens inside the model class if lazy)
model = TopViewModel("topview/final_best.pt")


def _draw_pins(img, boxes, pin_color=(0, 0, 255), box_color=(0, 255, 0)):
    """Draw centroids (pins) and optional boxes on the image.

    Args:
        img: BGR image (numpy array)
        boxes: list of dicts with keys x1,y1,x2,y2,cx,cy,conf
        pin_color: BGR tuple for pin (default red)
        box_color: BGR tuple for box (default green)

    Returns:
        Annotated image (numpy array)
    """
    out = img.copy()
    for i, b in enumerate(boxes):
        x1, y1, x2, y2 = b.get('x1'), b.get('y1'), b.get('x2'), b.get('y2')
        cx, cy = b.get('cx'), b.get('cy')
        conf = b.get('conf', None)

        # draw box (optional)
        if x1 is not None:
            cv2.rectangle(out, (x1, y1), (x2, y2), box_color, 2)

        # draw pin (small filled circle)
        if cx is not None:
            cv2.circle(out, (cx, cy), 8, pin_color, -1)
            # draw outline for visibility
            cv2.circle(out, (cx, cy), 10, (255, 255, 255), 2)

        # label with index and confidence
        label = f"#{i}"
        if conf is not None:
            label += f" {conf:.2f}"
        if cx is not None:
            cv2.putText(out, label, (cx + 12, cy + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    return out


@router.post("/detect")
async def detect_trees(file: UploadFile = File(...)):
    """Return detection metadata as JSON (existing behavior)."""
    img_bytes = await file.read()
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    boxes = model.detect_trees(img)

    return JSONResponse({
        "count": len(boxes),
        "centroids": boxes,
    })


@router.post("/detect/image")
async def detect_trees_image(file: UploadFile = File(...)):
    """Return the input image annotated with pins at detected tree centroids.

    Response: image/png bytes
    """
    img_bytes = await file.read()
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    boxes = model.detect_trees(img)

    annotated = _draw_pins(img, boxes)

    # encode to PNG
    success, buf = cv2.imencode('.png', annotated)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode annotated image")

    return StreamingResponse(io.BytesIO(buf.tobytes()), media_type='image/png')
