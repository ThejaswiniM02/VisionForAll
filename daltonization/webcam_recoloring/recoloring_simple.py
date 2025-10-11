import cv2
import numpy as np
from daltonlens import simulate

def apply_daltonlens_simulation(frame, deficiency='deutan', severity=1.0, model='Machado2009'):
    # Convert BGR to RGB for daltonlens
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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
    simulated = sim.simulate_cvd(rgb, deficiency=deficiency_enum, severity=severity)

    # Simple correction (daltonization fallback)
    error = rgb.astype(np.float32) - simulated.astype(np.float32)
    corrected = rgb.astype(np.float32) + 0.7 * error
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)

    # Convert corrected back to BGR for OpenCV display
    return cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)

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

        daltonized_frame = apply_daltonlens_simulation(frame, deficiency='deutan', severity=1.0, model='Machado2009')

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
        cv2.putText(combined, 'Daltonized', (new_width + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Original vs Daltonized", combined)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
