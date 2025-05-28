# License Plate Detection with Groq API

This Flask application provides a web interface for detecting and validating Sri Lankan vehicle license plates using the Groq API. Upload images of vehicles to detect license plate numbers and check their status against a mock database.

## Features

- Image upload functionality
- Sri Lankan license plate detection using Groq's LLM API
- Vehicle information validation
- Modern, responsive web interface
- JSON-based vehicle database

## Sri Lankan License Plate Format

The application recognizes standard Sri Lankan license plate formats:

1. Province-Letters-Numbers (e.g., WP-CAR-1234)
2. Province-Category-Letters-Numbers (e.g., WP-PB-AB-1234)
3. Province-Letters/Category-Numbers (e.g., WP-KV-3374)

Common province codes:
- WP: Western Province
- CP: Central Province
- SP: Southern Province
- NP: Northern Province
- EP: Eastern Province
- NW: North Western Province
- SG: Sabaragamuwa Province
- UP: Uva Province

## Prerequisites

- Python 3.8 or higher
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd car-license-plate-detection
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# For macOS/Linux:
source venv/bin/activate
# For Windows:
venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add your Groq API key:
```bash
GROQ_API_KEY=your_api_key_here
```

## Running the Application

1. Make sure your virtual environment is activated:
```bash
# For macOS/Linux:
source venv/bin/activate
# For Windows:
venv\Scripts\activate
```

2. Start the Flask server:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:8080
```

## Usage

1. Access the web interface through your browser
2. Click "Choose File" or drag and drop an image containing a Sri Lankan vehicle license plate
3. Click "Process Image" to analyze the image
4. View the results:
   - Detected license plate number in standard Sri Lankan format
   - Vehicle status (Valid, Invalid, Expired, or Has Cases)
   - Detailed vehicle information if available

## Vehicle Database

The application uses a JSON-based vehicle database located at `data/vehicle_database.json`. The database structure is as follows:

```json
{
    "PROVINCE-CATEGORY-NUMBER": {
        "valid": boolean,
        "expired": boolean,
        "cases": boolean
    }
}
```

### Database Fields

- `valid`: Indicates if the license plate is currently valid
- `expired`: Indicates if the license has expired
- `cases`: Indicates if there are any pending cases against the vehicle

### Example Entry

```json
{
    "WP-KV-3374": {
        "valid": true,
        "expired": false,
        "cases": false
    }
}
```

### Modifying the Database

To add or modify vehicle entries:
1. Open `data/vehicle_database.json`
2. Add or modify entries following the Sri Lankan license plate format
3. Ensure the JSON is valid before saving
4. The application will automatically load changes on restart

## Error Handling

The application includes error handling for:
- Invalid image files
- Missing database file
- Invalid JSON format
- API processing errors
- Unrecognized license plate formats

## Security Notes

- Store your Groq API key securely in the `.env` file
- Never commit the `.env` file to version control
- This is a development server - use a production WSGI server for deployment

## License

[Add your license information here] 