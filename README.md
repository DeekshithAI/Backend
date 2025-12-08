# Coconut Tree Health Analysis - Backend API

FastAPI backend for drone-based coconut tree health monitoring with ML models for detection and disease classification.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database (.env file)
DATABASE_URL=postgresql://user:password@localhost:5432/vaayu_drishti

# Initialize database
python init_db.py

# Start server
python -m uvicorn main:app --reload

# API Documentation
http://127.0.0.1:8000/docs
```

## 📁 Project Structure

```
backend/
├── api/                    # API routers
│   ├── drone_router.py     # Drone pipeline endpoints
│   ├── farmer_router.py    # Farmer CRUD
│   └── survey_router.py    # Survey management
├── db/                     # Database layer
│   ├── models.py           # SQLAlchemy models
│   ├── crud.py             # CRUD operations
│   └── database.py         # DB connection
├── sideview/               # Health detection
│   ├── model.py            # TensorFlow model
│   ├── aggregator.py       # Health aggregation
│   └── phase2_best.h5      # Trained model
├── topview/                # Tree detection
│   ├── model.py            # YOLO + rendering
│   └── final_best.pt       # Trained YOLO
└── uploads/                # Image storage
```

## 🔌 API Endpoints

### Farmer Management

- `POST /api/farmer/register` - Register farmer
- `GET /api/farmer/all` - List all farmers
- `GET /api/farmer/{id}` - Get farmer details
- `DELETE /api/farmer/{id}` - Delete farmer

### Survey Management

- `POST /api/survey/start` - Create survey (reuses deleted IDs)
- `GET /api/survey/{id}/trees` - List trees
- `GET /api/survey/{id}/report` - Health report
- `DELETE /api/survey/{farmer_id}/survey/{survey_id}` - Delete survey
- `DELETE /api/survey/{survey_id}/tree/{tree_id}` - Delete tree

### Drone Pipeline

- `POST /api/drone/topview` - Upload image, detect trees
- `POST /api/drone/sideview` - Upload video, analyze health
- `POST /api/drone/sideview/update-tree` - Update tree health
- `POST /api/drone/sideview/mock-batch` - Batch updates
- `GET /api/drone/{survey_id}/image` - Get annotated image

## 🔄 Workflow

```
1. Register Farmer → POST /api/farmer/register
2. Start Survey → POST /api/survey/start
3. Upload Topview → POST /api/drone/topview (detects trees, assigns numbers)
4. Upload Sideview → POST /api/drone/sideview (analyzes health per tree)
5. View Results → GET /api/survey/{id}/report (health statistics)
6. View Image → GET /api/drone/{id}/image (colored health map)
```

## 🎨 Health System

### Three Levels

- **Healthy** (Green) - No diseases
- **Unhealthy** (Orange) - Non-critical diseases
- **Critical** (Red) - Critical diseases (bud_rot, stem_bleeding, bud_root_dropping)

### Pin Rendering

- 40px colored circles with numbers
- Collision avoidance prevents overlap
- Real-time image generation

## 🗄️ Database Schema

**Farmer**: id, name, phone, created_at  
**Survey**: id (reusable), farmer_id, land_location, total_trees, topview_image_path  
**Tree**: id, survey_id, tree_number (reusable), cx, cy, final_status, final_health, critical_alert  
**TreePart**: id, tree_id, part_name, status, confidence

## ✨ Key Features

- ✅ ID Reuse (surveys & tree numbers)
- ✅ Critical disease detection
- ✅ Multi-part health aggregation
- ✅ Pin collision avoidance
- ✅ Batch processing
- ✅ Real-time image rendering
- ✅ Secure deletions (require farmer_id)

## 🧠 ML Models

**TopView**: YOLO (`final_best.pt`) - Tree detection  
**SideView**: TensorFlow (`phase2_best.h5`) - Health classification (stem/bud/leaves)

## 🛠️ Environment

```env
DATABASE_URL=postgresql://user:password@localhost:5432/vaayu_drishti
```

## 📦 Dependencies

FastAPI, SQLAlchemy, PostgreSQL, TensorFlow 2.10, Ultralytics YOLO, OpenCV, Pydantic

## 📄 License

MIT
