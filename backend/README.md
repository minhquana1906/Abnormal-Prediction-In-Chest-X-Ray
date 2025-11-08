# Backend - Chest X-Ray Abnormality Detection API

FastAPI backend for image processing and disease detection.

## Structure

```
backend/
├── src/
│   ├── api/              # FastAPI application
│   ├── filters/          # Custom image processing filters
│   ├── models/           # YOLO detector wrapper
│   ├── utils/            # Utilities and helpers
│   └── config/           # Configuration constants
├── models/               # Model weights storage (ONLY persistent storage)
└── pyproject.toml        # Dependencies
```

## Dependencies

- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server
- **Pillow**: Image I/O
- **NumPy**: Array operations for custom filter implementations
- **Ultralytics**: YOLOv11s inference
- **Loguru**: Logging

## Setup

**Note**: This project uses a single `pyproject.toml` at the repository root with dependency groups.

```bash
# From repository root
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
uv pip install -e ".[backend]"
```

## Running

```bash
# From repository root
uvicorn backend.src.api.main:app --reload --port 8000
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

## Features

- **Image Upload**: POST /upload - Upload X-ray images (max 10MB, PNG/JPG/JPEG)
- **Filter Processing**: POST /filter/apply - Apply 8 custom image filters
- **Disease Detection**: POST /detect/analyze - Detect 14 disease classes with YOLOv11s
- **Health Check**: GET /health - API status

## Implementation Status

- [ ] Phase 1: Setup ✅ COMPLETED
- [ ] Phase 2: Foundational (T009-T022) - IN PROGRESS
- [ ] Phase 3: User Story 1 - Filters (T023-T042)
- [ ] Phase 4: User Story 2 - Detection (T043-T057)
- [ ] Phase 6: Integration & Polish (T075-T095)
