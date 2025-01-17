from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageEnhance
import pydicom
import numpy as np
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

current_image = None  # To store the current image object
current_metadata = {}  # To store metadata


def normalize_pixel_data(pixel_array):
    pixel_array = pixel_array.astype(float)
    pixel_array = 255 * (pixel_array - np.min(pixel_array)) / (np.ptp(pixel_array))
    return pixel_array.astype(np.uint8)


@app.route("/upload", methods=["POST"])
def upload_dicom():
    global current_image, current_metadata

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Load DICOM file
    dicom_data = pydicom.dcmread(filepath)
    current_metadata = {
        "PatientName": str(dicom_data.PatientName),
        "StudyDate": dicom_data.StudyDate,
        "Modality": dicom_data.Modality,
        "Dimensions": dicom_data.pixel_array.shape,
    }

    # Convert pixel data to an image
    pixel_array = dicom_data.pixel_array
    normalized_image = normalize_pixel_data(pixel_array)
    current_image = Image.fromarray(normalized_image)

    output_path = os.path.join(OUTPUT_FOLDER, "original_image.png")
    current_image.save(output_path)

    return jsonify({"message": "File uploaded successfully", "metadata": current_metadata}), 200


@app.route("/metadata", methods=["GET"])
def get_metadata():
    if not current_metadata:
        return jsonify({"error": "No DICOM file loaded"}), 400
    return jsonify(current_metadata), 200


@app.route("/image", methods=["GET"])
def get_image():
    if current_image is None:
        return jsonify({"error": "No DICOM file loaded"}), 400
    output_path = os.path.join(OUTPUT_FOLDER, "current_image.png")
    current_image.save(output_path)
    return send_file(output_path, mimetype="image/png")


@app.route("/adjust", methods=["POST"])
def adjust_image():
    global current_image

    if current_image is None:
        return jsonify({"error": "No DICOM file loaded"}), 400

    data = request.json
    if not data:
        return jsonify({"error": "No adjustment parameters provided"}), 400

    brightness = data.get("brightness", 1.0)
    contrast = data.get("contrast", 1.0)

    enhancer = ImageEnhance.Brightness(current_image)
    current_image = enhancer.enhance(brightness)

    enhancer = ImageEnhance.Contrast(current_image)
    current_image = enhancer.enhance(contrast)

    output_path = os.path.join(OUTPUT_FOLDER, "adjusted_image.png")
    current_image.save(output_path)

    return jsonify({"message": "Image adjusted successfully"}), 200


@app.route("/crop", methods=["POST"])
def crop_image():
    global current_image

    if current_image is None:
        return jsonify({"error": "No image loaded"}), 400

    # Get cropping parameters from request (x, y, width, height)
    x = request.json.get("x", 0)
    y = request.json.get("y", 0)
    width = request.json.get("width", 100)
    height = request.json.get("height", 100)

    cropped_image = current_image.crop((x, y, x + width, y + height))

    output_path = os.path.join(OUTPUT_FOLDER, "cropped_image.png")
    cropped_image.save(output_path)

    return jsonify({"message": "Image cropped successfully"}), 200


@app.route("/zoom", methods=["POST"])
def zoom_image():
    global current_image

    if current_image is None:
        return jsonify({"error": "No image loaded"}), 400

    # Get zoom factor from request (default: 1.0)
    zoom_factor = request.json.get("zoom_factor", 1.0)
    width, height = current_image.size
    new_width = int(width * zoom_factor)
    new_height = int(height * zoom_factor)

    zoomed_image = current_image.resize((new_width, new_height))
    output_path = os.path.join(OUTPUT_FOLDER, "zoomed_image.png")
    zoomed_image.save(output_path)

    return jsonify({"message": "Image zoomed successfully"}), 200


@app.route("/pan", methods=["POST"])
def pan_image():
    global current_image

    if current_image is None:
        return jsonify({"error": "No image loaded"}), 400

    # Get pan offset parameters (dx, dy)
    dx = request.json.get("dx", 0)
    dy = request.json.get("dy", 0)

    width, height = current_image.size
    panned_image = current_image.transform(
        (width, height), Image.AFFINE, (1, 0, dx, 0, 1, dy)
    )

    output_path = os.path.join(OUTPUT_FOLDER, "panned_image.png")
    panned_image.save(output_path)

    return jsonify({"message": "Image panned successfully"}), 200


@app.route("/window_level", methods=["POST"])
def window_level():
    global current_image

    if current_image is None:
        return jsonify({"error": "No image loaded"}), 400

    # Get window/level values from request
    window = request.json.get("window", 255)
    level = request.json.get("level", 127)

    # Apply window/level adjustment
    pixel_array = np.array(current_image)
    adjusted_pixels = np.clip(pixel_array, level - window / 2, level + window / 2)

    adjusted_image = Image.fromarray(adjusted_pixels.astype(np.uint8))
    output_path = os.path.join(OUTPUT_FOLDER, "window_level_image.png")
    adjusted_image.save(output_path)

    return jsonify({"message": "Window/Level adjustment applied successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
