import cv2
import numpy as np

# Color Blindness transformation matrices
CVD_MATRICES = {
    'protanopia': np.array([[0.567, 0.433, 0.000],
                            [0.558, 0.442, 0.000],
                            [0.000, 0.242, 0.758]]),

    'deuteranopia': np.array([[0.625, 0.375, 0.000],
                              [0.700, 0.300, 0.000],
                              [0.000, 0.300, 0.700]]),

    'tritanopia': np.array([[0.950, 0.050, 0.000],
                            [0.000, 0.433, 0.567],
                            [0.000, 0.475, 0.525]])
}

def apply_cvd_filter(frame, matrix):
    """Apply color transformation matrix to simulate CVD."""
    frame = frame / 255.0
    transformed = np.dot(frame.reshape(-1, 3), matrix.T)
    transformed = np.clip(transformed, 0, 1)
    return (transformed.reshape(frame.shape) * 255).astype(np.uint8)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not access the webcam.")
        return

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Apply all 3 CVD transformations
        protanopia = apply_cvd_filter(frame_rgb, CVD_MATRICES['protanopia'])
        deuteranopia = apply_cvd_filter(frame_rgb, CVD_MATRICES['deuteranopia'])
        tritanopia = apply_cvd_filter(frame_rgb, CVD_MATRICES['tritanopia'])

        # Resize all frames for layout
        height, width = frame_rgb.shape[:2]
        small_size = (width // 2, height // 2)

        original_small = cv2.resize(frame_rgb, small_size)
        protanopia_small = cv2.resize(protanopia, small_size)
        deuteranopia_small = cv2.resize(deuteranopia, small_size)
        tritanopia_small = cv2.resize(tritanopia, small_size)

        # Combine into a 2x2 grid
        top_row = np.hstack((original_small, protanopia_small))
        bottom_row = np.hstack((deuteranopia_small, tritanopia_small))
        grid_rgb = np.vstack((top_row, bottom_row))

        # Convert to BGR for OpenCV display
        grid_bgr = cv2.cvtColor(grid_rgb, cv2.COLOR_RGB2BGR)

        # Add labels
        cv2.putText(grid_bgr, "Original", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(grid_bgr, "Protanopia", (small_size[0]+10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(grid_bgr, "Deuteranopia", (10, small_size[1]+25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(grid_bgr, "Tritanopia", (small_size[0]+10, small_size[1]+25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("CVD Simulation Grid", grid_bgr)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
