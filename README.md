# Face Recognition Attendance System

A Python-based attendance system that uses face recognition to identify registered students and automatically record attendance.

## Features

- Real-time face recognition
- Register students using webcam
- Automatic attendance marking
- Prevents duplicate attendance
- Detects unknown faces
- Attendance dashboard
- Search attendance records
- Filter attendance by date
- Attendance percentage
- Export to CSV
- Export to Excel
- Generate PDF reports
- Manage unknown face images
- SQLite database

## Dashboard

[Dashboard](screenshots/dashboard.png)

## Technologies

- Python
- OpenCV
- face_recognition
- dlib
- Tkinter
- SQLite
- NumPy
- OpenPyXL
- ReportLab
- Pillow

## Project Structure

```text
FaceRecognitionSystem/

─attendance/
  * Attendance data

─ database/
  * Database files

─ known_faces/
  * Registered face images

─ unknown_faces/
  * Unknown face images

─ attendance.py
  * Attendance management

─ database.py
  * Database operations

─ recognition.py
  * Face recognition

─ register.py
  * Face registration

─ utils.py
  * Utility functions

─ main.py
  * Main recognition system

─ dashboard.py
  * GUI dashboard

─ app.py
  * Application entry point

─ requirements.txt
  * Python dependencies

─ README.md
  * Project documentation

─ .gitignore
  * Ignored files and folders
