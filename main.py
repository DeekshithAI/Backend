# backend/main.py

from fastapi import FastAPI
from topview.router import router as topview_router
from sideview.router import router as sideview_router
from api.drone_router import router as drone_router
from api.farmer_router import router as farmer_router
from api.survey_router import router as survey_router

app = FastAPI(title="Coconut Tree Analyzer Backend")

app.include_router(topview_router)
app.include_router(sideview_router)
app.include_router(drone_router)
app.include_router(farmer_router)
app.include_router(survey_router)