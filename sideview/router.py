# backend/sideview/router.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os

from .model import SideViewModel
from .aggregator import aggregate_health_robust   # ← NEW IMPORT

router = APIRouter(prefix="/sideview", tags=["Side-View Disease Detection"])

model = SideViewModel()

@router.post("/analyze")
async def analyze_tree(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = model.predict(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)

    return JSONResponse(result)



# ---------------------------------------------------------------------
# NEW ENDPOINT — For aggregating results from video (stem/bud/leaves)
# ---------------------------------------------------------------------
@router.post("/analyze-video")
async def analyze_video(data: dict):
    """
    Input JSON:
    {
        "stem": [ {"status": "...", "confidence": 0.9}, ... ],
        "bud":  [ ... ],
        "leaves": [ ... ]
    }
    """
    try:
        result = aggregate_health_robust(data)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------


