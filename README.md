# Car License Plate Detection System

This project implements a real-time car license plate detection and recognition system using YOLOv8 for detection and EasyOCR for text recognition. The system is built with Flask and provides a web interface for both real-time video processing and image uploads.

## Features

- Real-time license plate detection using YOLOv8
- License plate text recognition using EasyOCR
- Web interface for video feed and image uploads
- Vehicle status checking system
- Support for both video streaming and image processing

## Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for better performance)
- Webcam or video source

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd car-license-plate-detection
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── data.yaml             # YOLO dataset configuration
├── requirements.txt      # Python dependencies
├── split_dataset.py      # Dataset splitting utility
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS, etc.)
└── yolov8n.pt           # Pre-trained YOLO model
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Choose between:
   - Real-time video feed processing
   - Image upload and processing

## Model Training

1. Prepare your dataset in the following structure:
```
dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

2. Update the `data.yaml` file with your dataset paths

3. Run the training script:
```bash
yolo train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

4. Monitor the training progress and adjust parameters as needed.

5. Once training is complete, evaluate the model using:
```bash
yolo val model=path/to/trained/model.pt data=data.yaml
```

6. Use the trained model for inference in your application.

## API Endpoints

- `/`: Main web interface
- `/video_feed`: Real-time video stream
- `/process_image`: Image processing endpoint

## Dependencies

- ultralytics>=8.0.0
- opencv-python>=4.8.0
- easyocr>=1.7.0
- flask>=2.0.0
- pillow>=10.0.0
- numpy>=1.24.0

## 📝 License

This project is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).

## 👏 Credits

Created by [Rumeasiyan](https://github.com/rumeasiyan)

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contributors

<div align="center">
  <a href="https://github.com/rumeasiyan">
    <img src="https://github.com/rumeasiyan.png" width="100" style="border-radius: 50%;">
    <br>
    <sub><b>Rumeasiyan</b></sub>
  </a>
</div>

## Acknowledgments

- YOLOv8 for object detection
- EasyOCR for text recognition
- Flask for web framework 