from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from .database import Base

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    surveys = relationship("Survey", back_populates="farmer")


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    land_location = Column(String)
    total_trees = Column(Integer, nullable=True)
    topview_image_path = Column(String, nullable=True)
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farmer = relationship("Farmer", back_populates="surveys")
    trees = relationship("Tree", back_populates="survey")


class Tree(Base):
    __tablename__ = "trees"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    tree_number = Column(Integer, nullable=False)

    final_status = Column(String, nullable=True)    # healthy / unhealthy / critical
    final_health_percentage = Column(Float, nullable=True)
    critical_alert = Column(Boolean, default=False)
    
    cx = Column(Integer, nullable=True)  # centroid x from top-view detection
    cy = Column(Integer, nullable=True)  # centroid y from top-view detection
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    survey = relationship("Survey", back_populates="trees")
    parts = relationship("TreePart", back_populates="tree")


class TreePart(Base):
    __tablename__ = "tree_parts"

    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, ForeignKey("trees.id"), nullable=False)

    part_name = Column(String, nullable=False)  # stem, bud, leaves
    status = Column(String, nullable=False)  # e.g. "healthy", "whitefly"
    confidence = Column(Float, nullable=False)
    extra = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    tree = relationship("Tree", back_populates="parts")
