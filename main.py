"""
main.py
-------
Entry point for the Face Recognition Attendance System.

Flow:

    Webcam
       ↓
    Face Detection
       ↓
    Face Recognition
       ↓
    ┌───────────────────────┐
    │                       │
    Known Person       Unknown Person
       ↓                    ↓
    Attendance          Save Face
       ↓                    ↓
    SQLite + CSV       unknown_faces/
                         + DB log

Controls while running:
    q  - quit
    r  - print today's attendance report
"""

import os
import argparse
from datetime import datetime

import cv2
import face_recognition

import database
import recognition
import attendance
import utils


# =========================
# SETTINGS
# =========================

UNKNOWN_DIR = "unknown_faces"

FRAME_RESIZE_SCALE = 0.25

PROCESS_EVERY_N_FRAMES = 3

UNKNOWN_SAVE_COOLDOWN_SECONDS = 30

FACE_MARGIN = 40


# =========================
# SAVE UNKNOWN FACE
# =========================

def save_unknown_face(
    frame,
    face_location
):
    """
    Crop and save an unknown face.

    face_location:
        (top, right, bottom, left)

    Returns:
        saved file path or None
    """

    os.makedirs(
        UNKNOWN_DIR,
        exist_ok=True
    )

    top, right, bottom, left = face_location

    height, width = frame.shape[:2]

    # Add margin around face

    top = max(
        0,
        top - FACE_MARGIN
    )

    right = min(
        width,
        right + FACE_MARGIN
    )

    bottom = min(
        height,
        bottom + FACE_MARGIN
    )

    left = max(
        0,
        left - FACE_MARGIN
    )

    face_crop = frame[
        top:bottom,
        left:right
    ]

    if face_crop.size == 0:

        return None

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"unknown_{timestamp}.jpg"
    )

    save_path = os.path.join(
        UNKNOWN_DIR,
        filename
    )

    success = cv2.imwrite(
        save_path,
        face_crop
    )

    if not success:

        return None

    return save_path


# =========================
# MAIN RECOGNITION
# =========================

def run(camera_index: int = 0):

    # Create required folders

    utils.ensure_dirs()

    os.makedirs(
        UNKNOWN_DIR,
        exist_ok=True
    )

    # Initialize database

    database.init_db()

    # Load known faces

    known_encodings, known_names = (
        recognition.load_known_faces()
    )

    print(
        f"[i] Known people loaded: {len(known_names)}"
    )

    # Open webcam

    cam = cv2.VideoCapture(
        camera_index
    )

    if not cam.isOpened():

        raise RuntimeError(
            "Could not access the webcam."
        )

    print()
    print(
        "[i] Face Recognition System Started"
    )
    print(
        "[i] Press 'q' to quit."
    )
    print(
        "[i] Press 'r' for today's attendance report."
    )
    print()

    frame_count = 0

    # Last time an unknown face was saved

    last_unknown_save = 0

    # Prevent repeated attendance processing

    already_greeted_today = set()

    while True:

        ret, frame = cam.read()

        if not ret:

            print(
                "[!] Failed to read from webcam."
            )

            break

        frame_count += 1

        # Copy original frame for display

        display_frame = frame.copy()

        # ==================================
        # PROCESS EVERY Nth FRAME
        # ==================================

        if (
            frame_count %
            PROCESS_EVERY_N_FRAMES
            == 0
        ):

            # Resize frame for faster processing

            small_frame = cv2.resize(
                frame,
                (
                    0,
                    0
                ),
                fx=FRAME_RESIZE_SCALE,
                fy=FRAME_RESIZE_SCALE
            )

            # Convert BGR → RGB

            rgb_small = cv2.cvtColor(
                small_frame,
                cv2.COLOR_BGR2RGB
            )

            # ==================================
            # FACE DETECTION
            # ==================================

            face_locations = (
                face_recognition.face_locations(
                    rgb_small
                )
            )

            face_encodings = (
                face_recognition.face_encodings(
                    rgb_small,
                    face_locations
                )
            )

            # ==================================
            # PROCESS EACH FACE
            # ==================================

            for (
                face_location,
                face_encoding
            ) in zip(
                face_locations,
                face_encodings
            ):

                # ==================================
                # FACE RECOGNITION
                # ==================================

                name = recognition.match_face(
                    face_encoding,
                    known_encodings,
                    known_names
                )

                # ==================================
                # SCALE COORDINATES
                # ==================================

                scale = int(
                    1 /
                    FRAME_RESIZE_SCALE
                )

                top, right, bottom, left = (
                    face_location
                )

                top *= scale
                right *= scale
                bottom *= scale
                left *= scale

                # ==================================
                # KNOWN PERSON
                # ==================================

                if name != "Unknown":

                    color = (
                        0,
                        200,
                        0
                    )

                    # Mark attendance once

                    if name not in already_greeted_today:

                        marked = attendance.mark(
                            name
                        )

                        if marked:

                            already_greeted_today.add(
                                name
                            )

                            print(
                                f"[+] Attendance marked: {name}"
                            )

                # ==================================
                # UNKNOWN PERSON
                # ==================================

                else:

                    color = (
                        0,
                        0,
                        255
                    )

                    current_time = (
                        datetime.now().timestamp()
                    )

                    # Check cooldown

                    if (
                        current_time -
                        last_unknown_save
                        >
                        UNKNOWN_SAVE_COOLDOWN_SECONDS
                    ):

                        save_path = save_unknown_face(
                            frame,
                            (
                                top,
                                right,
                                bottom,
                                left
                            )
                        )

                        if save_path:

                            date, time_str = (
                                utils.now_date_time()
                            )

                            # Log in database

                            database.log_unknown_detection(
                                save_path,
                                date,
                                time_str
                            )

                            last_unknown_save = (
                                current_time
                            )

                            print(
                                f"[!] Unknown face saved: {save_path}"
                            )

                # ==================================
                # DRAW FACE BOX
                # ==================================

                cv2.rectangle(
                    display_frame,
                    (
                        left,
                        top
                    ),
                    (
                        right,
                        bottom
                    ),
                    color,
                    2
                )

                # ==================================
                # LABEL BACKGROUND
                # ==================================

                label_top = max(
                    bottom - 30,
                    0
                )

                cv2.rectangle(
                    display_frame,
                    (
                        left,
                        label_top
                    ),
                    (
                        right,
                        bottom
                    ),
                    color,
                    cv2.FILLED
                )

                # ==================================
                # LABEL
                # ==================================

                cv2.putText(
                    display_frame,
                    name,
                    (
                        left + 6,
                        bottom - 8
                    ),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.6,
                    (
                        255,
                        255,
                        255
                    ),
                    1
                )

        # ==================================
        # DISPLAY CAMERA
        # ==================================

        cv2.imshow(
            "Face Recognition Attendance System",
            display_frame
        )

        # ==================================
        # KEYBOARD CONTROLS
        # ==================================

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        # Quit

        if key == ord("q"):

            break

        # Today's report

        elif key == ord("r"):

            today = (
                datetime.now().strftime(
                    "%Y-%m-%d"
                )
            )

            attendance.print_report(
                today
            )

    # ==================================
    # CLEANUP
    # ==================================

    cam.release()

    cv2.destroyAllWindows()

    print(
        "[i] Camera closed."
    )


# =========================
# PROGRAM ENTRY
# =========================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Face Recognition "
            "Attendance System"
        )
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Webcam device index"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help=(
            "Print full attendance "
            "report and exit"
        )
    )

    args = parser.parse_args()

    # ==================================
    # REPORT MODE
    # ==================================

    if args.report:

        utils.ensure_dirs()

        database.init_db()

        attendance.print_report()

    # ==================================
    # CAMERA MODE
    # ==================================

    else:

        run(
            camera_index=args.camera
        )