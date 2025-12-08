# Coconut Tree Analyzer Backend

FastAPI backend for drone-based tree surveying and health analysis. Integrates YOLO for tree detection and TensorFlow for disease classification.

## 🚀 Quick Start

### Local Development

```bash
# Clone and install
git clone <repo-url>
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vaayu_drishti

# Start server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Visit http://127.0.0.1:8000/docs
```

### Docker Compose (Recommended)

```bash
docker-compose up -d
# Starts PostgreSQL and FastAPI backend
```

## 📁 Project Structure

```
backend/
├── api/
│   ├── drone_router.py        # Drone endpoints with validation
│   ├── farmer_router.py       # Farmer CRUD
│   └── survey_router.py       # Survey management
├── topview/
│   ├── model.py               # YOLO tree detection
│   ├── final_best.pt          # YOLO weights
│   └── router.py              # Topview endpoints
├── sideview/
│   ├── model.py               # TensorFlow classifier
│   ├── phase2_best.h5         # TensorFlow weights
│   ├── aggregator.py          # Health aggregation
│   └── router.py              # Sideview endpoints
├── db/
│   ├── models.py              # SQLAlchemy ORM
│   ├── crud.py                # Database operations
│   └── database.py            # DB setup
├── schemas/
│   └── sideview_schemas.py    # Pydantic models
├── tests/
│   └── test_validation_helpers.py  # Unit tests
├── main.py                    # FastAPI app + middleware
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container image
├── docker-compose.yml         # Local/staging setup
├── README.md                  # This file
└── .github/workflows/
    └── python-ci.yml          # GitHub Actions CI/CD
```

## 🔌 API Endpoints

### Health & Status

- `GET /health` - Service health check
- `GET /` - API documentation links

### Drone Endpoints (all require `farmer_id`)

- `POST /api/drone/topview` - Upload image, detect trees
- `POST /api/drone/sideview` - Upload video, analyze health
- `POST /api/drone/sideview/update-tree` - Update single tree part (validated)
- `POST /api/drone/sideview/mock` - Mock single update for testing
- `POST /api/drone/sideview/mock-batch` - Batch updates with partial success
- `GET /api/drone/{farmer_id}/{survey_id}/annotated-image` - Get generated image
- `GET /api/drone/{farmer_id}/{survey_id}/image` - Get original image

### Management

- `/api/farmer/` - Farmer CRUD operations
- `/api/survey/` - Survey management
- `/topview/` - Additional topview operations
- `/sideview/` - Additional sideview operations

## ✅ Input Validation

All sideview endpoints validate inputs and return 400 on errors:

| Field         | Valid Values                                   | Example                       |
| ------------- | ---------------------------------------------- | ----------------------------- |
| `part_name`   | stem, bud, leaves                              | "stem" or "STEM" (normalized) |
| `status`      | healthy, unhealthy, critical, or disease types | "healthy", "bud_rot"          |
| `tree_number` | positive integer (> 0)                         | 1, 5, 100                     |
| `confidence`  | float [0.0, 1.0]                               | 0.95, 0.5                     |

**Invalid request example:**

```bash
curl -X POST http://localhost:8000/api/drone/sideview/mock \
  -F part_name=ROOT  # Invalid!
```

**Response (400):**

```json
{
  "detail": "Invalid part_name 'root'. Must be one of: {'stem', 'bud', 'leaves'}"
}
```

## 🎨 Health System

### Status Levels

- **Healthy** (🟢 Green) - No diseases detected
- **Unhealthy** (🟠 Orange) - Non-critical diseases
- **Critical** (🔴 Red) - Critical diseases present

### Critical Diseases

- `bud_rot`
- `stem_bleeding`
- `bud_root_dropping`

### Aggregation

Health calculated from tree parts (stem, bud, leaves):

- **All healthy** → 100% healthy (GREEN)
- **Some unhealthy** → % of diseased parts (ORANGE)
- **Critical disease** → 0% health + alert (RED)

## 🧪 Testing

### Unit Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=.
```

### Integration Tests

```bash
# Terminal 1
python -m uvicorn main:app --reload

# Terminal 2
python test_validation.py
```

### Code Quality

```bash
pip install flake8 ruff black
ruff check .
black --check .
```

## 🐳 Docker

### Build Image

```bash
docker build -t vaayu-backend:latest .
```

### Run Locally

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  vaayu-backend:latest
```

### Docker Compose (Dev/Staging)

```bash
docker-compose up -d      # Start with PostgreSQL
docker-compose logs -f    # View logs
docker-compose down       # Stop
```

## 🚀 Deployment

### Production Checklist

- [ ] Environment variables set (DATABASE_URL, LOG_LEVEL)
- [ ] Database migrations run
- [ ] Model weights loaded and verified
- [ ] Health check endpoint working (`GET /health`)
- [ ] Logging configured and monitored
- [ ] Rate limiting enabled
- [ ] CORS restricted to allowed origins
- [ ] Backups scheduled for database
- [ ] Load balancer configured with `/health` checks

### Recommended Setup

```yaml
Container Runtime: Docker / Kubernetes
Python Version: 3.10+
Replicas: 2-3 (for high availability)
Health Check: GET /health (30s interval)
Resources:
  CPU: 2-4 cores per instance
  RAM: 2-4 GB (model memory)
  GPU: Optional (faster inference)
```

## 📊 Monitoring

### Built-in

- Structured JSON logging
- Request timing and status tracking
- Health endpoint with model status

### Recommended Tools

- **Logs**: ELK Stack, CloudWatch, Datadog
- **Metrics**: Prometheus + Grafana
- **Errors**: Sentry
- **APM**: New Relic, Jaeger

## 🔐 Security

- ✅ Input validation on all endpoints
- ✅ farmer_id authorization checks
- ✅ SQLAlchemy ORM (SQL injection prevention)
- 🔲 TODO: JWT authentication
- 🔲 TODO: Rate limiting
- 🔲 TODO: CORS restrictions
- 🔲 TODO: Secrets manager integration

## 🗄️ Database

PostgreSQL 15+ required.

**Connection string format:**

```
postgresql://username:password@hostname:5432/database_name
```

**Environment variable:**

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vaayu_drishti
```

## 🛠️ Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/vaayu_drishti

# Optional
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
PYTHON_ENV=development      # development, staging, production
WORKERS=4                   # Uvicorn workers (production)
```

## 📚 API Documentation

Interactive docs available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🤝 Frontend Integration

### Example: Update Tree Health

```javascript
async function updateTreeHealth(
  farmerId,
  surveyId,
  treeNumber,
  partName,
  status,
  confidence
) {
  const formData = new FormData();
  formData.append("farmer_id", farmerId);
  formData.append("survey_id", surveyId);
  formData.append("tree_number", treeNumber);
  formData.append("part_name", partName);
  formData.append("status", status);
  formData.append("confidence", confidence);

  const res = await fetch("/api/drone/sideview/mock", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    console.error("Error:", error.detail);
    return;
  }

  const result = await res.json();
  console.log("Updated:", result.aggregated_health);
}
```

### Example: Batch Update

```javascript
async function batchUpdate(farmerId, surveyId, trees) {
  const res = await fetch("/api/drone/sideview/mock-batch", {
    method: "POST",
    body: new FormData({
      farmer_id: farmerId,
      survey_id: surveyId,
      trees_json: JSON.stringify(trees),
    }),
  });

  const result = await res.json();

  // Check per-item results
  result.results.forEach((item) => {
    if (item.success) {
      console.log(`✓ Tree ${item.tree_number}`);
    } else {
      console.error(`✗ Tree ${item.tree_number}: ${item.error}`);
    }
  });
}
```

## 🐛 Troubleshooting

| Issue               | Solution                                                              |
| ------------------- | --------------------------------------------------------------------- |
| Port 8000 in use    | `lsof -i :8000 \| grep LISTEN \| awk '{print $2}' \| xargs kill -9`   |
| Model load error    | Check files exist: `topview/final_best.pt`, `sideview/phase2_best.h5` |
| DB connection error | Verify `DATABASE_URL` and PostgreSQL is running                       |
| Docker build fails  | Run `docker-compose build --no-cache`                                 |

## 📝 License

[Your License Here]

## 👥 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feat/your-feature`)
3. Write tests for new features
4. Commit changes (`git commit -am 'Add feature'`)
5. Push to branch (`git push origin feat/your-feature`)
6. Submit pull request to `develop`

---

**Questions?** Open an issue or contact the development team.

## 📦 Dependencies

FastAPI, SQLAlchemy, PostgreSQL, TensorFlow 2.10, Ultralytics YOLO, OpenCV, Pydantic

## 📄 License

MIT
