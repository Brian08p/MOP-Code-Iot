# -*- coding: utf-8 -*-
"""test.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1h6UE-9hNTBxaMRAZeLxmERsWqLRBKP_r
"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

#  Load trained model

model_path = '/content/drive/MyDrive/vehicle_classification/vehicle_classifier_mobilenet.keras'
model = load_model(model_path)

#  Load class labels (based on training folders)
class_dir = '/content/drive/MyDrive/vehicle_classification/vehicle_classification_datasets/train'
class_labels = sorted(os.listdir(class_dir))

#  Prediction function
def predict_vehicle_image(img_path, model, class_labels, threshold=0.6):
    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array, verbose=0)
    confidence = np.max(prediction)
    class_idx = np.argmax(prediction)

    if confidence < threshold:
        label = "Unknown Vehicle"
    else:
        label = f"{class_labels[class_idx]} ({confidence*100:.1f}%)"

    #  Show result
    plt.imshow(img)
    plt.axis('off')
    plt.title(f"Prediction: {label}")
    plt.show()
    return label

predict_vehicle_image('/content/drive/MyDrive/vehicle_classification/vehicle_classification_datasets/test/class_12/adidnauman-tripleroadtrain-001.jpeg', model, class_labels)

predict_vehicle_image('/content/drive/MyDrive/vehicle_classification/processed_images/class_2/qasimzia-caravan-196.jpg', model, class_labels)

predict_vehicle_image('/content/drive/MyDrive/vehicle_classification/vehicle_classification_datasets/test/class_10/class_10_0048.png', model, class_labels)

! pip install ultralytics

import cv2
import numpy as np
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import os
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import load_img

video_path = '/content/drive/MyDrive/vehicle_classification/test.mp4'

model_path = '/content/drive/MyDrive/vehicle_classification/vehicle_classifier_mobilenet.keras'
output_path = '/content/drive/MyDrive/vehicle_classification/Annotated_Accident_Video.mp4'
class_labels = sorted(os.listdir('/content/drive/MyDrive/vehicle_classification/vehicle_classification_datasets/train'))

yolo_model = YOLO('yolov8n.pt')
classifier = load_model(model_path)

cap = cv2.VideoCapture(video_path)
frame_count = 0

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

#  Output video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #  YOLO detection
    results = yolo_model(frame, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck (COCO IDs)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            crop = frame[y1:y2, x1:x2]

            try:
                crop_resized = cv2.resize(crop, (224, 224))
                img_array = img_to_array(crop_resized) / 255.0
                img_array = np.expand_dims(img_array, axis=0)

                prediction = classifier.predict(img_array, verbose=0)
                confidence = np.max(prediction)
                class_idx = np.argmax(prediction)

                if confidence < 0.6:
                    label = "Unknown Vehicle"
                else:
                    label = f"{class_labels[class_idx]} ({confidence*100:.1f}%)"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            except Exception as e:
                print(f"Skipping frame due to error: {e}")
            frame_count += 1


    out.write(frame)
print(f" Total frames processed: {frame_count}")


cap.release()
out.release()
print(" Annotated video saved to:", output_path)

!pip install git+https://github.com/ultralytics/ultralytics.git@main

!pip install deep_sort_realtime

from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort


yolo_model = YOLO('yolov8n.pt')

tracker = DeepSort(max_age=30, n_init=2, nms_max_overlap=1.0)