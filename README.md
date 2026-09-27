# Face Recognition Attendance System

A webcam-based attendance system: detects and recognizes faces, marks
attendance automatically for known people, and logs unrecognized faces
for review.

```
Webcam → Face Detection → Face Recognition
              ┌────────────┴────────────┐
         Known Person               Unknown Person
              ↓                          ↓
       Mark Attendance             Save Detection
              ↓
       SQLite Database
              ↓
       Dashboard / Report
```

## Project Structure

```
FaceRecognitionSystem/
│
├── main.py            # Entry point: runs the live webcam recognition loop
├── register.py        # CLI tool to register a new known face
├── recognition.py      # Loads known faces, matches faces against them
├── database.py         # SQLite schema + read/write operations
├── attendance.py        # Attendance-marking logic and report/dashboard
├── utils.py             # Shared helpers (CSV logging, timestamps, dirs)
│
├── known_faces/          # One image per registered person (name.jpg)
├── attendance/
│   └── attendance.csv    # CSV backup of every attendance record
├── database/
│   └── attendance.db     # SQLite database (created on first run)
│
├── requirements.txt
└── README.md
```

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > `dlib` (a `face_recognition` dependency) needs CMake and a C++ compiler
   > to build. On Windows, installing via `conda install -c conda-forge dlib`
   > is often easier than pip.

## Usage

### 1. Register known people

From a webcam photo:
```bash
python register.py --name "Jane Doe" --webcam
```
Press **SPACE** to capture, **ESC** to cancel.

From an existing image file:
```bash
python register.py --name "Jane Doe" --image path/to/jane.jpg
```

This saves the photo to `known_faces/` and adds the person to the database.
Use one clear, front-facing photo per person for best accuracy.

### 2. Run the live attendance system

```bash
python main.py
```

- Detected known faces are boxed in **green** with their name, and attendance
  is marked once per person per day.
- Detected unknown faces are boxed in **red**, and a snapshot is saved to
  `unknown_faces/` (logged in the database, throttled to avoid duplicate saves).

**Controls:**
- `q` — quit
- `r` — print today's attendance report to the console

### 3. View the attendance report / dashboard

```bash
python main.py --report
```
Prints a full, date-grouped attendance report from the database.
Raw data is also available in `attendance/attendance.csv` and
`database/attendance.db` if you want to build a richer dashboard
(e.g. a Flask or Streamlit app) on top of it later.

## Notes & Limitations

- Recognition accuracy depends heavily on lighting and the quality of the
  registered reference photo. Re-register with a clearer photo if a person
  is frequently misidentified as "Unknown".
- The `TOLERANCE` value in `recognition.py` controls match strictness
  (lower = stricter, fewer false positives; higher = more lenient).
- This system stores face images and encodings locally. If deploying this
  for real attendance tracking, consider your organization's data privacy
  and biometric-data regulations (e.g. GDPR, BIPA) before rollout.
