<<<<<<< HEAD
# AI Face Verification Assistant 🏦

A hackathon-ready prototype for bank officers to verify customer identity using live face capture and ID photo comparison.

## 🛠️ Tech Stack

### Backend (Python 3.13)
- **FastAPI**: High-performance async web framework.
- **DeepFace**: State-of-the-art face recognition (uses **ArcFace** model).
- **OpenCV**: Computer vision for detecting variations (glasses, lighting, occlusion).
- **SQLite**: Zero-config database for verification audit logs.
- **Uvicorn**: ASIC web server.

### Frontend
- **HTML5 / JavaScript**: Pure vanilla implementation (no build steps required).
- **CSS3**: Custom "Glassmorphism" dark UI with CSS variables and animations.
- **Features**: Live webcam access, drag-and-drop upload, SVG animations.

---

## 🚀 How to Run

### 1. Prerequisites
- Python 3.10 or higher (Tested on 3.13)
- Webcam (for live capture)

### 2. Setup (One-time)
Open your terminal in the project folder:

```bash
cd "d:\banker assistant"
pip install -r requirements_hackathon.txt
```

*(Note: The first run will automatically download the ArcFace model (~150MB).)*

### 3. Start the Backend
Run the following command in a terminal:

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start the Frontend
Open a new terminal and run:

```bash
cd frontend-react
npm install
npm run dev
```

### 5. Open the App
Go to your browser and visit the URL shown in the frontend terminal (usually `http://localhost:5173`).

---

## 📂 Project Structure

```
d:\banker assistant\
├── backend/
│   ├── app.py                  # Main API entry point
│   ├── face_service.py         # DeepFace embedding & similarity logic
│   ├── variation_detector.py   # OpenCV detection (glasses, lighting, etc.)
│   ├── explanation_engine.py   # Generates banker-friendly text
│   ├── decision_engine.py      # Approval thresholds
│   └── logger_db.py            # SQLite database manager
├── frontend/
│   └── index.html              # Complete single-page UI
├── requirements_hackathon.txt  # Minimal dependencies
└── README.md                   # This file
```

## 🧠 Key Features for Hackathon Judges
1. **Variation Handling**: Detects glasses, lighting issues, and partial occlusion; relaxes thresholds automatically.
2. **Explainability**: Returns human-readable reasons ("High match, but glasses detected").
3. **Audit Trail**: Logs every verification attempt to SQLite for compliance.
4. **Zero-Config**: Works out of the box with `pip install` and `python run`.
=======
# banker_ai
>>>>>>> 1d84a60846f15cc91747b85b79d9d950bb7a42cf
