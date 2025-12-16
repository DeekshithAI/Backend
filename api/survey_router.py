from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from db.database import get_db
from db import crud

router = APIRouter(prefix="/api/survey", tags=["Survey Management"])

class SurveyStart(BaseModel):
    farmer_id: int
    land_location: Optional[str] = None

class TreeAdd(BaseModel):
    tree_number: int
    cx: float
    cy: float

@router.post("/start")
def start_survey(body: SurveyStart, db: Session = Depends(get_db)):
    """
    Create a new survey for a farmer
    """
    # Verify farmer exists
    farmer = crud.get_farmer(db, body.farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {body.farmer_id} not found")
    
    survey = crud.create_survey(db, body.farmer_id, body.land_location)
    return {
        "survey_id": survey.id,
        "farmer_id": survey.farmer_id,
        "land_location": survey.land_location,
        "created_at": survey.created_at
    }

@router.post("/{survey_id}/add-tree")
def add_tree_manually(survey_id: int, body: TreeAdd, db: Session = Depends(get_db)):
    """
    Manually add a tree to a survey (for testing without drone upload)
    """
    # Verify survey exists
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    
    # Create tree
    tree = crud.create_tree(db, survey_id, body.tree_number, body.cx, body.cy)
    
    return {
        "tree_id": tree.id,
        "survey_id": survey_id,
        "tree_number": tree.tree_number,
        "cx": tree.cx,
        "cy": tree.cy,
        "created_at": tree.created_at
    }

@router.delete("/{farmer_id}/survey/{survey_id}")
def delete_survey(farmer_id: int, survey_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific survey belonging to a farmer
    """
    from db.models import Survey
    import os
    
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.farmer_id == farmer_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found for this farmer")
    
    # Delete uploaded files
    survey_dir = f"uploads/surveys/{survey_id}"
    if os.path.exists(survey_dir):
        import shutil
        shutil.rmtree(survey_dir)
    
    db.delete(survey)
    db.commit()
    
    return {"message": f"Survey {survey_id} deleted successfully", "survey_id": survey_id, "farmer_id": farmer_id}


@router.delete("/{survey_id}/tree/{tree_id}")
def delete_tree(survey_id: int, tree_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific tree from a survey. The tree number becomes available for reuse.
    """
    from db.models import Tree
    import os
    import cv2
    from topview.model import draw_overlay
    
    tree = db.query(Tree).filter(Tree.id == tree_id, Tree.survey_id == survey_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    
    deleted_tree_number = tree.tree_number
    
    # Delete the tree (do NOT renumber others)
    db.delete(tree)
    
    # Update survey total_trees count
    survey = crud.get_survey(db, survey_id)
    if survey:
        remaining_count = db.query(Tree).filter(Tree.survey_id == survey_id).count()
        survey.total_trees = remaining_count
    
    db.commit()
    
    # Regenerate annotated image without the deleted tree
    if survey and survey.topview_image_path and os.path.exists(survey.topview_image_path):
        original_path = survey.topview_image_path.replace("topview_annotated.jpg", "topview_raw.jpg")
        if os.path.exists(original_path):
            img = cv2.imread(original_path)
            if img is not None:
                remaining_trees = db.query(Tree).filter(Tree.survey_id == survey_id).all()
                centroids = []
                for t in remaining_trees:
                    centroids.append({
                        "cx": t.cx,
                        "cy": t.cy,
                        "tree_number": t.tree_number,
                        "final_status": t.final_status,
                        "critical_alert": t.critical_alert
                    })
                draw_overlay(img, centroids, out_path=survey.topview_image_path, pin_radius=40)
    
    return {
        "message": f"Tree #{deleted_tree_number} deleted (number can be reused)",
        "tree_id": tree_id,
        "deleted_tree_number": deleted_tree_number,
        "remaining_trees": remaining_count if survey else 0,
        "image_updated": True
    }


@router.get("/{survey_id}/trees")
def get_survey_trees(survey_id: int, db: Session = Depends(get_db)):
    """
    Get all trees in a survey with their health data and parts
    """
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    
    from db.models import Tree
    trees = db.query(Tree).filter(Tree.survey_id == survey_id).order_by(Tree.tree_number).all()
    
    result = []
    for tree in trees:
        # Get parts for each tree
        parts = crud.get_parts_for_tree(db, tree.id)
        
        result.append({
            "tree_id": tree.id,
            "tree_number": tree.tree_number,
            "cx": tree.cx,
            "cy": tree.cy,
            "final_status": tree.final_status,
            "final_health_percentage": tree.final_health_percentage,
            "critical_alert": tree.critical_alert,
            "parts": [
                {
                    "part_name": p.part_name,
                    "status": p.status,
                    "confidence": p.confidence,
                    "extra": p.extra,
                    "timestamp": p.timestamp
                } for p in parts
            ],
            "created_at": tree.created_at
        })
    
    return {
        "survey_id": survey_id,
        "total_trees": survey.total_trees,
        "trees": result
    }

@router.get("/{survey_id}/report")
def get_survey_report(survey_id: int, db: Session = Depends(get_db)):
    """
    Generate comprehensive survey report with aggregated statistics
    """
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    
    from db.models import Tree
    trees = db.query(Tree).filter(Tree.survey_id == survey_id).all()
    
    if not trees:
        return {
            "survey_id": survey_id,
            "farmer_id": survey.farmer_id,
            "land_location": survey.land_location,
            "total_trees": survey.total_trees,
            "trees_analyzed": 0,
            "message": "No trees analyzed yet"
        }
    
    # Calculate statistics
    total = len(trees)
    healthy_count = sum(1 for t in trees if t.final_status == "healthy")
    unhealthy_count = sum(1 for t in trees if t.final_status == "unhealthy" and not t.critical_alert)
    critical_count = sum(1 for t in trees if t.critical_alert or t.final_status == "critical")
    
    # Calculate average health (only from trees with valid data)
    valid_health = [t.final_health_percentage for t in trees if t.final_health_percentage is not None]
    avg_health = sum(valid_health) / len(valid_health) if valid_health else 0.0
    
    # Overall status: healthy, unhealthy, or critical (no moderate)
    if critical_count > 0:
        overall_status = "critical"
    elif unhealthy_count > healthy_count:
        overall_status = "unhealthy"
    else:
        overall_status = "healthy"
    
    return {
        "survey_id": survey_id,
        "farmer_id": survey.farmer_id,
        "land_location": survey.land_location,
        "total_trees": survey.total_trees,
        "trees_analyzed": total,
        "healthy_count": healthy_count,
        "unhealthy_count": unhealthy_count,
        "critical_count": critical_count,
        "average_health_percentage": round(avg_health, 2),
        "overall_status": overall_status,
        "topview_image_path": survey.topview_image_path,
        "created_at": survey.created_at
    }
