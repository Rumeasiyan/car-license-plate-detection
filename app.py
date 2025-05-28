from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import base64
from groq import Groq
from dotenv import load_dotenv
import os
import io
from PIL import Image
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load vehicle database from JSON file
def load_vehicle_database():
    try:
        with open('data/vehicle_database.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: Vehicle database file not found")
        return {}
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in vehicle database file")
        return {}

# Load the vehicle database
vehicle_data = load_vehicle_database()

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

def process_image_with_groq(image_data):
    try:
        # Convert image data to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create chat completion with Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this image and extract the Sri Lankan vehicle license plate number. All vehicles are Sri Lankan. Format the output in the standard Sri Lankan format with sections separated by hyphens (-). Common formats are:\n\n1. Province-Letters-Numbers (e.g., WP-CAR-1234)\n2. Province-Category-Letters-Numbers (e.g., WP-PB-AB-1234)\n3. Province-Letters/Category-Numbers (e.g., WP-KV-3374)\n\nReturn only the formatted license plate number without any additional text or explanation."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            }
                        }
                    ]
                },
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        
        # Extract the license plate number from the response
        plate_text = chat_completion.choices[0].message.content.strip()
        return plate_text.upper()
    
    except Exception as e:
        print(f"Error in Groq API processing: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

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
        # Read the image file
        image_data = file.read()
        
        # Process image with Groq API
        plate_text = process_image_with_groq(image_data)
        
        # Get vehicle information
        vehicle_info = vehicle_data.get(plate_text)
        status_text = get_vehicle_status(vehicle_info)[0]
        
        response_data = {
            'plate_number': plate_text,
            'vehicle_info': vehicle_info if vehicle_info else None,
            'status': status_text
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

if __name__ == '__main__':
    if not os.environ.get("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY environment variable is not set")
    app.run(host='0.0.0.0', port=8080, debug=True) 