# Frontend - Chest X-Ray Abnormality Detection UI

Streamlit web interface for chest X-ray analysis.

## Structure

```
frontend/
├── src/
│   ├── app.py                   # Main Streamlit application
│   ├── pages/
│   │   ├── filter_processing.py # Tab 1: Image filters
│   │   └── detection.py         # Tab 2: Disease detection
│   ├── components/
│   │   ├── image_uploader.py    # File upload widget
│   │   ├── filter_selector.py   # Filter selection UI
│   │   ├── result_display.py    # Image results display
│   │   └── health_card.py       # Health info cards
│   └── utils/
│       ├── api_client.py        # Backend API client
│       └── ui_helpers.py        # Vietnamese message formatting
└── pyproject.toml               # Dependencies
```

## Dependencies

- **Streamlit**: Web UI framework
- **Requests**: HTTP client for backend communication
- **Pillow**: Image handling
- **NumPy**: Image array operations
- **Loguru**: Logging

## Setup

**Note**: This project uses a single `pyproject.toml` at the repository root with dependency groups.

```bash
# From repository root
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install frontend dependencies
uv pip install -e ".[frontend]"
```

## Running

```bash
# From repository root
cd frontend
streamlit run src/app.py --server.port 8501
```

The app will be available at http://localhost:8501

## Features

### Tab 1: Image Filter Processing
- Upload chest X-ray images
- Select from 8 image processing filters:
  - Sobel Edge Detection
  - Canny Edge Detection
  - Gaussian Blur
  - Median Filter
  - Histogram Equalization
  - Fourier Transform
  - Discrete Cosine Transform (DCT)
  - Otsu Thresholding
- View side-by-side comparison
- Download processed images

### Tab 2: Disease Detection
- Upload chest X-ray images
- AI-powered detection of 14 disease classes
- Bounding boxes with confidence levels (3-tier: high/medium/low)
- Vietnamese health information and warnings
- Download annotated images

## Implementation Status

- [ ] Phase 1: Setup ✅ COMPLETED
- [ ] Phase 2: Foundational (T015-T018) - IN PROGRESS
- [ ] Phase 3: User Story 1 - Filter UI (T037-T042)
- [ ] Phase 4: User Story 2 - Detection UI (T051-T057)
- [ ] Phase 6: Integration & Polish (T075-T095)

## Notes

- All error messages in Vietnamese
- Backend must be running at http://localhost:8000
- Images processed in memory (no file storage)
- Max file size: 10MB
