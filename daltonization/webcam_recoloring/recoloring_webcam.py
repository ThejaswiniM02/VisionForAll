import cv2
import numpy as np

# Color space transformation matrices
cb_matrices = {
    "d": np.array([[1, 0, 0], [1.10104433, 0, -0.00901975], [0, 0, 1]], dtype=np.float32),
    "p": np.array([[0, 0.90822864, 0.008192], [0, 1, 0], [0, 0, 1]], dtype=np.float32),
    "t": np.array([[1, 0, 0], [0, 1, 0], [-0.15773032, 1.19465634, 0]], dtype=np.float32),
}
rgb2lms = np.array([[0.3904725 , 0.54990437, 0.00890159],
                    [0.07092586, 0.96310739, 0.00135809],
                    [0.02314268, 0.12801221, 0.93605194]], dtype=np.float32)
lms2rgb = np.array([[ 2.85831110e+00, -1.62870796e+00, -2.48186967e-02],
                    [-2.10434776e-01,  1.15841493e+00,  3.20463334e-04],
                    [-4.18895045e-02, -1.18154333e-01,  1.06888657e+00]], dtype=np.float32)

def transform_colorspace(img, mat):
    return img @ mat.T

def gamma_correction(img, gamma=2.2):
    img = img / 255.0
    corrected = np.power(img, gamma)
    return corrected

def inverse_gamma_correction(img, gamma=2.2):
    corrected = np.power(img, 1.0/gamma)
    corrected = np.clip(corrected * 255, 0, 255).astype(np.uint8)
    return corrected

def simulate(rgb, deficit='d'):
    lms = transform_colorspace(rgb, rgb2lms)
    sim_lms = transform_colorspace(lms, cb_matrices[deficit])
    sim_rgb = transform_colorspace(sim_lms, lms2rgb)
    return np.clip(sim_rgb, 0, 1)

def daltonize(rgb, deficit='d'):
    sim_rgb = simulate(rgb, deficit)
    err2mod = np.array([[0,0,0], [0.7,1,0], [0.7,0,1]], dtype=np.float32)
    err = transform_colorspace(rgb - sim_rgb, err2mod)
    dtpn = err + rgb
    return np.clip(dtpn, 0, 1)

def enhance_contrast_lab(image_rgb):
    lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
    return enhanced_rgb

def apply_daltonization(frame_bgr, deficiency='d'):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    rgb = gamma_correction(rgb)

    daltonized = daltonize(rgb, deficiency)

    daltonized_disp = inverse_gamma_correction(daltonized)

    enhanced = enhance_contrast_lab(daltonized_disp)

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

        daltonized_frame = apply_daltonization(frame, deficiency='d')

        height, width = frame.shape[:2]
        new_width = width // 2
        new_height = height // 2
        frame_small = cv2.resize(frame, (new_width, new_height))
        daltonized_small = cv2.resize(daltonized_frame, (new_width, new_height))

        combined = np.hstack((frame_small, daltonized_small))

        cv2.putText(combined, 'Original', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(combined, 'Daltonized + Contrast', (new_width + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Original vs Daltonized", combined)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
