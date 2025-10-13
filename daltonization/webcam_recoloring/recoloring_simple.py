import cv2
import numpy as np
from daltonlens import simulate

def enhance_contrast_lab(image_rgb):
    lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
    return enhanced_rgb

def apply_daltonization(frame_bgr, deficiency='deutan', severity=1.0, model='Machado2009'):
    # Convert BGR to RGB for daltonlens
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    # Select simulation model
    if model == 'Machado2009':
        sim = simulate.Simulator_Machado2009()
    elif model == 'Brettel1997':
        sim = simulate.Simulator_Brettel1997()
    elif model == 'Vienot1999':
        sim = simulate.Simulator_Vienot1999()
    else:
        raise ValueError("Unknown model")

    deficiency_enum = simulate.Deficiency[deficiency.upper()]

    # Simulate color blindness perception
    simulated = sim.simulate_cvd(rgb, deficiency=deficiency_enum, severity=severity)

    # Daltonization: Calculate error and correct
    error = rgb.astype(np.float32) - simulated.astype(np.float32)
    corrected = rgb.astype(np.float32) + 0.7 * error
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)

    # Enhance contrast to improve visibility for colorblind users
    enhanced = enhance_contrast_lab(corrected)

    # Convert corrected & enhanced RGB back to BGR for OpenCV display
    return cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        return

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        daltonized_frame = apply_daltonization(frame, deficiency='deutan', severity=1.0, model='Machado2009')

        # Resize frames for side-by-side display (optional)
        height, width = frame.shape[:2]
        new_width = width // 2
        new_height = height // 2
        frame_small = cv2.resize(frame, (new_width, new_height))
        daltonized_small = cv2.resize(daltonized_frame, (new_width, new_height))

        # Concatenate horizontally
        combined = np.hstack((frame_small, daltonized_small))

        # Add labels on top of frames
        cv2.putText(combined, 'Original', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(combined, 'Daltonized + Contrast', (new_width + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Original vs Daltonized", combined)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
