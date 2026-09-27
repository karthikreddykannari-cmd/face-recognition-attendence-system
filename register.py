"""
register.py
------------
Standalone script to register a new person's face, either by
capturing a photo from the webcam or by importing an existing
image file. Saves the image into known_faces/ and records the
person in the database.

Usage:
    python register.py --name "John Doe" --webcam
    python register.py --name "John Doe" --image path/to/photo.jpg
"""

import argparse
import os
import shutil

import cv2
import face_recognition

import database
import utils

KNOWN_FACES_DIR = "known_faces"


def capture_from_webcam(name: str) -> str:
    """Open the webcam, let the user press SPACE to capture a photo."""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Could not access the webcam.")

    print("[i] Webcam open. Press SPACE to capture, ESC to cancel.")
    save_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")

    captured_path = None
    while True:
        ret, frame = cam.read()
        if not ret:
            break

        cv2.imshow("Register Face - press SPACE to capture", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            print("[!] Registration cancelled.")
            break
        elif key == 32:  # SPACE
            cv2.imwrite(save_path, frame)
            captured_path = save_path
            print(f"[✓] Photo captured and saved to {save_path}")
            break

    cam.release()
    cv2.destroyAllWindows()
    return captured_path


def import_image(name: str, image_path: str) -> str:
    """Copy an existing image file into known_faces/ under the person's name."""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    ext = os.path.splitext(image_path)[1].lower()
    dest = os.path.join(KNOWN_FACES_DIR, f"{name}{ext}")
    shutil.copy(image_path, dest)
    print(f"[✓] Image copied to {dest}")
    return dest


def verify_face_present(image_path: str) -> bool:
    """Confirm the saved image actually contains a detectable face."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    return len(encodings) > 0


def main():
    parser = argparse.ArgumentParser(description="Register a new known face.")
    parser.add_argument("--name", required=True, help="Person's name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--webcam", action="store_true", help="Capture photo from webcam")
    group.add_argument("--image", type=str, help="Path to an existing image file")
    args = parser.parse_args()

    utils.ensure_dirs()
    database.init_db()

    name = args.name.strip().replace(" ", "_")

    if args.webcam:
        image_path = capture_from_webcam(name)
    else:
        image_path = import_image(name, args.image)

    if not image_path:
        print("[!] No image saved. Registration aborted.")
        return

    if not verify_face_present(image_path):
        print("[!] Warning: no face detected in the saved image. "
              "Recognition will not work for this person until re-registered "
              "with a clearer photo.")
        return

    database.add_person(name, image_path)
    print(f"[✓] '{name}' registered successfully.")


if __name__ == "__main__":
    main()
