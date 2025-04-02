import os
import xml.etree.ElementTree as ET

# Define paths
ANNOTATIONS_DIR = "archive/annotations"
YOLO_LABELS_DIR = "yolo_labels"
os.makedirs(YOLO_LABELS_DIR, exist_ok=True)

# Class names
class_mapping = {"licence": 0}  # YOLO needs numeric labels

def convert_to_yolo_format(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    filename = root.find("filename").text.replace(".png", ".txt")
    
    size = root.find("size")
    img_w, img_h = int(size.find("width").text), int(size.find("height").text)
    
    yolo_labels = []
    
    for obj in root.findall("object"):
        bbox = obj.find("bndbox")
        xmin, ymin = int(bbox.find("xmin").text), int(bbox.find("ymin").text)
        xmax, ymax = int(bbox.find("xmax").text), int(bbox.find("ymax").text)

        # Normalize YOLO format: (class, x_center, y_center, width, height)
        x_center = (xmin + xmax) / (2 * img_w)
        y_center = (ymin + ymax) / (2 * img_h)
        width = (xmax - xmin) / img_w
        height = (ymax - ymin) / img_h

        yolo_labels.append(f"0 {x_center} {y_center} {width} {height}")

    # Save labels
    with open(os.path.join(YOLO_LABELS_DIR, filename), "w") as f:
        f.write("\n".join(yolo_labels))

# Convert all XML files
for xml_file in os.listdir(ANNOTATIONS_DIR):
    if xml_file.endswith(".xml"):
        convert_to_yolo_format(os.path.join(ANNOTATIONS_DIR, xml_file))
