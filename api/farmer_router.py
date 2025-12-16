# backend/api/farmer_router.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.database import get_db
from db import crud

router = APIRouter(prefix="/api/farmer", tags=["Farmer"])


class FarmerCreate(BaseModel):
    name: str
    phone: str | None = None


@router.post("/create")
def create_farmer(data: FarmerCreate, db: Session = Depends(get_db)):
    """Create a new farmer"""
    # If phone provided, try to find existing farmer to avoid duplicates
    farmer = None
    if data.phone:
        farmer = crud.get_farmer_by_phone(db, data.phone)
    if farmer is None:
        farmer = crud.create_farmer(db=db, name=data.name, phone=data.phone)
    return {
        "id": farmer.id, 
        "name": farmer.name, 
        "phone": farmer.phone,
        "created_at": farmer.created_at
    }


@router.get("/all")
def get_all_farmers(db: Session = Depends(get_db)):
    """Get all farmers"""
    from db.models import Farmer
    farmers = db.query(Farmer).all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "phone": f.phone,
            "created_at": f.created_at,
            "total_surveys": len(f.surveys)
        }
        for f in farmers
    ]


@router.get("/{farmer_id}")
def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Get specific farmer details"""
    farmer = crud.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    return {
        "id": farmer.id,
        "name": farmer.name,
        "phone": farmer.phone,
        "created_at": farmer.created_at,
        "total_surveys": len(farmer.surveys)
    }


@router.delete("/{farmer_id}")
def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Delete a farmer and all their surveys"""
    from db.models import Farmer
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    farmer_name = farmer.name
    db.delete(farmer)
    db.commit()
    
    return {"message": f"Farmer '{farmer_name}' deleted successfully", "farmer_id": farmer_id}


@router.get("/{farmer_id}/surveys")
def list_surveys(farmer_id: int, db: Session = Depends(get_db)):
    """Get all surveys for a farmer"""
    farmer = crud.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    return [
        {
            "survey_id": s.id,
            "location": s.land_location,
            "total_trees": s.total_trees,
            "topview_image": s.topview_image_path,
            "created_at": s.created_at
        }
        for s in farmer.surveys
    ]
