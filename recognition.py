"""
recognition.py
---------------
Loads known face encodings from the known_faces/ directory,
matches faces found in webcam frames, and provides utilities
for handling unknown faces.
"""

import os
from datetime import datetime

import cv2
import face_recognition


KNOWN_FACES_DIR = "known_faces"
UNKNOWN_FACES_DIR = "unknown_faces"

TOLERANCE = 0.6  # lower = stricter matching


def load_known_faces():
    """
    Scan known_faces/ for images, compute a face encoding for each,
    and return (encodings, names).

    Filename (without extension) is used as the person's name.

    Example:
        known_faces/john_doe.jpg -> "john_doe"
    """

    encodings = []
    names = []

    if not os.path.isdir(KNOWN_FACES_DIR):
        return encodings, names

    for filename in os.listdir(KNOWN_FACES_DIR):

        if not filename.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            continue

        path = os.path.join(
            KNOWN_FACES_DIR,
            filename
        )

        name = os.path.splitext(
            filename
        )[0]

        try:

            image = face_recognition.load_image_file(
                path
            )

            face_encs = face_recognition.face_encodings(
                image
            )

            if not face_encs:

                print(
                    f"[!] No face found in {filename}, skipping."
                )

                continue

            encodings.append(
                face_encs[0]
            )

            names.append(
                name
            )

        except Exception as e:

            print(
                f"[!] Error loading {filename}: {e}"
            )

    print(
        f"[i] Loaded {len(names)} known face(s): {names}"
    )

    return encodings, names


def match_face(
    face_encoding,
    known_encodings,
    known_names
):
    """
    Compare a single face encoding against all known encodings.

    Returns:
        Matched person's name
        OR
        "Unknown"
    """

    if not known_encodings:

        return "Unknown"

    matches = face_recognition.compare_faces(
        known_encodings,
        face_encoding,
        tolerance=TOLERANCE
    )

    distances = face_recognition.face_distance(
        known_encodings,
        face_encoding
    )

    if len(distances) == 0:

        return "Unknown"

    best_match_index = distances.argmin()

    if matches[best_match_index]:

        return known_names[
            best_match_index
        ]

    return "Unknown"


def ensure_unknown_faces_directory():
    """
    Create the unknown_faces directory if it doesn't exist.
    """

    os.makedirs(
        UNKNOWN_FACES_DIR,
        exist_ok=True
    )


def save_unknown_face(frame, face_location):
    """
    Save an unknown face from the webcam frame.

    face_location format:
        (top, right, bottom, left)

    Returns:
        Saved file path.
    """

    ensure_unknown_faces_directory()

    top, right, bottom, left = face_location

    # Add a small margin around the face
    margin = 30

    height, width = frame.shape[:2]

    top = max(
        0,
        top - margin
    )

    right = min(
        width,
        right + margin
    )

    bottom = min(
        height,
        bottom + margin
    )

    left = max(
        0,
        left - margin
    )

    face_image = frame[
        top:bottom,
        left:right
    ]

    if face_image.size == 0:

        return None

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"unknown_{timestamp}.jpg"
    )

    filepath = os.path.join(
        UNKNOWN_FACES_DIR,
        filename
    )

    success = cv2.imwrite(
        filepath,
        face_image
    )

    if success:

        print(
            f"[!] Unknown face saved: {filepath}"
        )

        return filepath

    print(
        "[!] Failed to save unknown face."
    )

    return None
