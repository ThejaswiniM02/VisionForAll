# backend/color_detection.py

import cv2
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans

def get_dominant_color(frame, k=3):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = img.reshape((-1, 3))

    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(img)

    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_

    count = Counter(labels)
    dominant_color = colors[count.most_common(1)[0][0]]

    print("All cluster colors (RGB):", colors)
    print("Dominant color (RGB):", dominant_color)

    return tuple(dominant_color)

def show_color_detection():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        dominant_color = get_dominant_color(frame)
        color_bgr = tuple(int(c) for c in dominant_color[::-1])  # Convert each channel to int explicitly
        cv2.rectangle(frame, (0, 0), (150, 150), color_bgr, -1)
        cv2.putText(frame, f"RGB: {dominant_color}", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        
        cv2.imshow('Color Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_color_detection()
