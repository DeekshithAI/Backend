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
        raw = model.predict(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)

    # Normalize model output to a richer structure expected by the app
    part_pred = raw.get('part') or raw.get('part_prediction')
    status_pred = raw.get('status') or raw.get('status_prediction')
    part_conf = raw.get('part_confidence') or raw.get('part_conf') or 0.0
    status_conf = raw.get('status_confidence') or raw.get('status_conf') or 0.0

    # Simple recommendation/fertilizer mapping (can be expanded later)
    recommendations_map = {
        'healthy': ["No immediate action needed. Monitor regularly."],
        'bud rot': ["Remove infected buds and improve drainage.", "Avoid overhead irrigation."],
        'leaf rot': ["Remove affected leaves and improve air circulation."],
        'grey leaf rot': ["Apply recommended fungicide and remove debris."],
        'whitefly': ["Use yellow sticky traps and consider neem oil sprays."],
        'bud root dropping': ["Inspect roots, improve soil drainage, and avoid waterlogging."],
        'stem bleeding': ["Prune damaged tissue and apply wound antiseptic."],
    }

    fertilizers_map = {
        'healthy': [],
        'bud rot': ["Balanced NPK fertilizer once infection controlled."],
        'leaf rot': ["Apply potassium-rich fertilizer to support recovery."],
        'grey leaf rot': ["Balanced NPK and micronutrients"],
        'whitefly': ["Use foliar micronutrients to boost plant vigor."],
        'bud root dropping': ["Organic matter and phosphorus-rich amendment."],
        'stem bleeding': ["Avoid heavy fertilization until healed."],
    }

    key = (str(status_pred) or '').lower()
    # Map by containing keywords for robustness
    recs = []
    ferts = []
    for k, v in recommendations_map.items():
        if k in key:
            recs = v
            break
    for k, v in fertilizers_map.items():
        if k in key:
            ferts = v
            break

    result = {
        'part': {'prediction': part_pred, 'confidence': float(part_conf)},
        'status': {'prediction': status_pred, 'confidence': float(status_conf)},
        'recommendations': recs,
        'fertilizers': ferts,
        'raw': raw,
    }

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


