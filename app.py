from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import easyocr
import numpy as np
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize YOLO model and EasyOCR
model = YOLO('runs/detect/train/weights/best.pt')  # Load the trained model
reader = easyocr.Reader(['en'])

# Mock database with more sample data
vehicle_data = {
    "KL01CA2555": {"valid": True, "expired": False, "cases": False},
    "AB1234": {"valid": False, "expired": True, "cases": True},
    "MH01AB1234": {"valid": True, "expired": False, "cases": False},
    "DL01CD5678": {"valid": False, "expired": True, "cases": False},
    "KA01EF9012": {"valid": True, "expired": False, "cases": True},
    "TN01GH3456": {"valid": False, "expired": False, "cases": True},
    "GJ01IJ7890": {"valid": True, "expired": True, "cases": False},
    "UP01KL2345": {"valid": True, "expired": False, "cases": False},
    "LIPE:36346": {"valid": True, "expired": False, "cases": False}
}

def get_vehicle_status(vehicle_info):
    if not vehicle_info:
        return "Not Available in System", (0, 165, 255)  # Orange for unknown/not in system
    
    if vehicle_info["valid"] and not vehicle_info["expired"] and not vehicle_info["cases"]:
        return "Valid", (0, 255, 0)  # Green for valid
    else:
        status_parts = []
        if not vehicle_info["valid"]:
            status_parts.append("Invalid")
        if vehicle_info["expired"]:
            status_parts.append("Expired")
        if vehicle_info["cases"]:
            status_parts.append("Has Cases")
        return " | ".join(status_parts), (0, 0, 255)  # Red for any issues

def process_frame(frame):
    if model is None:
        return frame, None
    
    # Run YOLO detection with confidence threshold based on training results
    results = model(frame, conf=0.25)  # Using 0.25 as it showed good results in training
    plate_text = None
    
    for result in results:
        for box in result.boxes:
            # Get box coordinates and confidence
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            
            # Extract license plate region
            plate_region = frame[y1:y2, x1:x2]
            if plate_region.size == 0:
                continue
            
            # Preprocess the plate region for better OCR
            # Convert to grayscale
            gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                
            # Perform OCR on both original and preprocessed images
            try:
                text_results = reader.readtext(thresh)  # Try preprocessed image first
                if not text_results:
                    text_results = reader.readtext(plate_region)  # Try original if no results
                
                if text_results:
                    plate_text = text_results[0][1].replace(" ", "").upper()
                    # Get vehicle status and color
                    vehicle_info = vehicle_data.get(plate_text)
                    status_text, color = get_vehicle_status(vehicle_info)
                    
                    # Draw bounding box and text
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw plate number with confidence
                    cv2.putText(frame, f"Plate: {plate_text} ({conf:.2f})", (x1, y1 - 25),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                    
                    # Draw status text
                    cv2.putText(frame, status_text, (x1, y1 - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            except Exception as e:
                print(f"Error in OCR: {str(e)}")
                continue
    
    return frame, plate_text

def generate_frames():
    camera = cv2.VideoCapture(0)  # Use 0 for default camera
    if not camera.isOpened():
        print("Error: Could not open camera")
        return

    while True:
        success, frame = camera.read()
        if not success:
            print("Error: Could not read frame")
            break

        # Process the frame with the model using the same logic as process_image
        results = model(frame, conf=0.25)  # Using same confidence threshold as training
        
        for result in results:
            for box in result.boxes:
                # Get box coordinates and confidence
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Extract license plate region
                plate_region = frame[y1:y2, x1:x2]
                if plate_region.size == 0:
                    continue
                
                # Preprocess the plate region for better OCR
                gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                    
                # Perform OCR on both original and preprocessed images
                try:
                    text_results = reader.readtext(thresh)  # Try preprocessed image first
                    if not text_results:
                        text_results = reader.readtext(plate_region)  # Try original if no results
                    
                    if text_results:
                        plate_text = text_results[0][1].replace(" ", "").upper()
                        # Get vehicle status and color from mock database
                        vehicle_info = vehicle_data.get(plate_text)
                        status_text, color = get_vehicle_status(vehicle_info)
                        
                        # Draw bounding box and text
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Draw plate number with confidence
                        cv2.putText(frame, f"Plate: {plate_text} ({conf:.2f})", (x1, y1 - 25),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        
                        # Draw status text
                        cv2.putText(frame, status_text, (x1, y1 - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                except Exception as e:
                    print(f"Error in OCR: {str(e)}")
                    continue

        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Read the image
        img_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': 'Failed to read image'}), 400

        # Resize image if it's too large (keeping aspect ratio)
        max_dimension = 1024
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale, fy=scale)

        # Process image with YOLO model
        results = model(img, conf=0.25)  # Using same confidence threshold as training
        
        if len(results[0].boxes) == 0:
            return jsonify({'error': 'No license plate detected'}), 404

        # Process the first detected plate
        box = results[0].boxes[0]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        
        # Extract and preprocess plate region
        plate_img = img[y1:y2, x1:x2]
        if plate_img.size == 0:
            return jsonify({'error': 'Invalid plate region'}), 400

        # Preprocess for OCR
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Try OCR on preprocessed image first
        text_results = reader.readtext(thresh)
        if not text_results:
            text_results = reader.readtext(plate_img)  # Try original if no results
        
        if not text_results:
            return jsonify({'error': 'Could not read license plate'}), 400

        plate_text = text_results[0][1].replace(" ", "").upper()
        vehicle_info = vehicle_data.get(plate_text)
        
        response_data = {
            'plate_number': plate_text,
            'confidence': float(conf),
            'vehicle_info': vehicle_info if vehicle_info else None,
            'status': get_vehicle_status(vehicle_info)[0] if vehicle_info else "Not Available in System"
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def load_model():
    global model
    try:
        model_path = 'runs/detect/train7/weights/best.pt'
        if os.path.exists(model_path):
            model = YOLO(model_path)
            print(f"Successfully loaded model from {model_path}")
        else:
            print(f"Error: Model file not found at {model_path}")
            print("Please make sure you have trained the model and the file exists.")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print("Please check if the model file is corrupted or if you have the correct permissions.")

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=8080, debug=True) 