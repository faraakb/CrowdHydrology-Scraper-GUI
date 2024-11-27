import cv2
import cvlib as cv
import os
import shutil
# Paths to the YOLO files
yolo_cfg_path = 'yolov4.cfg'
yolo_weights_path = 'yolov4.weights'
yolo_names_path = 'coco.names'

# Load YOLO model
net = cv2.dnn.readNetFromDarknet(yolo_cfg_path, yolo_weights_path)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Read class names from the coco.names file
with open(yolo_names_path, 'r') as f:
    class_names = f.read().strip().split('\n')

def detect_objects(image_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to open image file {image_path}")
        return False

    # Prepare the image for YOLO
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    # Run forward pass
    layer_names = net.getLayerNames()
    try:
        output_layer_names = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except TypeError:
        output_layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    outputs = net.forward(output_layer_names)

    # Process the outputs
    boxes, confidences, class_ids = [], [], []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = int(scores.argmax())
            confidence = scores[class_id]
            if confidence > 0.5:
                box = detection[0:4] * [image.shape[1], image.shape[0], image.shape[1], image.shape[0]]
                centerX, centerY, width, height = box.astype('int')
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maxima suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    person_detected = False
    if len(indices) > 0:
        for i in indices.flatten():
            if class_names[class_ids[i]] == 'person':
                person_detected = True
                x, y, w, h = boxes[i]
                label = str(class_names[class_ids[i]])
                confidence = str(round(confidences[i], 2))
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, label + ' ' + confidence, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return person_detected

def clear_folder(folder_path):
    """
    Clears the contents of the specified folder.

    Args:
    folder_path (str): The path to the folder to be cleared.
    """
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Iterate over all the files and subdirectories in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        try:
            # If it's a file, remove it
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # If it's a directory, remove it and all its contents
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Deletion Unsuccesful")

folder_path = 'messages_with_media'
dir1 = "has_people"
dir2 = "no_people"
clear_folder(dir1)
clear_folder(dir2)
if not os.path.exists(dir2):
    os.makedirs(dir2)
restricted = [".idea", ".venv", ".git", "coco.names", "crowd-hydroicon.png", "cvdetectorv3.py", "dropdown2.py", "face_detection.jpg", "test_newdrop.py", "testfil.py", "yolov4.cfg", "yolov4.weights", "__pycache__", "store_tokens.py", "dropdownv4.py", "has_people.zip"]
parent = r"C:\Users\faraz\PycharmProjects\testIDE"
for folder in os.listdir(parent):
    if folder in restricted or not os.listdir(folder):
        continue
    for filename in os.listdir(folder):
    # Construct full file path
        file_path = os.path.join(folder, filename)
        if detect_objects(file_path):
            shutil.copy2(file_path, dir1)
            print("Person detected in this image " + file_path)

