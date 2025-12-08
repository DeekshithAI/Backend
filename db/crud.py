from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models, schemas


# ------------------ FARMER ------------------
def create_farmer(db: Session, name: str, phone: str = None):
    db_farmer = models.Farmer(name=name, phone=phone)
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def get_farmer(db: Session, farmer_id: int):
    return db.get(models.Farmer, farmer_id)


def get_farmer_by_phone(db: Session, phone: str):
    return db.query(models.Farmer).filter(models.Farmer.phone == phone).first()


# ------------------ SURVEY ------------------
def create_survey(db: Session, farmer_id: int, land_location: str = None):
    # Find the lowest available survey ID (to reuse deleted IDs)
    existing_ids = db.query(models.Survey.id).all()
    used_ids = {sid[0] for sid in existing_ids}
    
    # Find first available ID
    new_id = 1
    while new_id in used_ids:
        new_id += 1
    
    db_survey = models.Survey(
        id=new_id,  # Manually assign ID
        farmer_id=farmer_id,
        land_location=land_location
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


def get_survey(db: Session, survey_id: int):
    return db.get(models.Survey, survey_id)


def get_surveys_by_farmer(db: Session, farmer_id: int):
    return db.query(models.Survey).filter(models.Survey.farmer_id == farmer_id).all()


def update_survey_topview_info(db: Session, survey_id: int, total_trees: int = None, 
                                topview_image_path: str = None, extra_data: dict = None):
    db_survey = db.get(models.Survey, survey_id)
    if not db_survey:
        return None
    if total_trees is not None:
        db_survey.total_trees = total_trees
    if topview_image_path is not None:
        db_survey.topview_image_path = topview_image_path
    if extra_data is not None:
        db_survey.extra_data = extra_data
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


# ------------------ TREES ------------------
def create_tree(db: Session, survey_id: int, tree_number: int, cx: int = None, cy: int = None):
    db_tree = models.Tree(
        survey_id=survey_id,
        tree_number=tree_number,
        cx=cx,
        cy=cy
    )
    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)
    return db_tree


def get_tree(db: Session, tree_id: int):
    return db.get(models.Tree, tree_id)


def get_trees_by_survey(db: Session, survey_id: int):
    return db.execute(select(models.Tree).where(models.Tree.survey_id == survey_id)).scalars().all()


def update_tree_health(db: Session, tree_id: int, final_health: float, 
                       final_status: str, critical_alert: bool = False):
    db_tree = db.get(models.Tree, tree_id)
    if not db_tree:
        return None
    db_tree.final_health_percentage = final_health
    db_tree.final_status = final_status
    db_tree.critical_alert = critical_alert
    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)
    return db_tree


# ------------------ TREE PARTS ------------------
def add_tree_part(db: Session, tree_id: int, part_name: str, status: str, 
                  confidence: float, extra: dict = None):
    db_part = models.TreePart(
        tree_id=tree_id,
        part_name=part_name,
        status=status,
        confidence=confidence,
        extra=extra or {}
    )
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part


def get_parts_for_tree(db: Session, tree_id: int):
    return db.execute(select(models.TreePart).where(models.TreePart.tree_id == tree_id)).scalars().all()
