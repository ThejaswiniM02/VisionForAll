import cv2
import numpy as np
import matplotlib.pyplot as plt

# Color space matrices and transformations based on the referenced code
def transform_colorspace(img, mat):
    return img @ mat.T

def simulate(rgb, color_deficit="d"):
    cb_matrices = {
        "d": np.array([[1, 0, 0], [1.10104433,  0, -0.00901975], [0, 0, 1]], dtype=np.float32),
        "p": np.array([[0, 0.90822864, 0.008192], [0, 1, 0], [0, 0, 1]], dtype=np.float32),
        "t": np.array([[1, 0, 0], [0, 1, 0], [-0.15773032,  1.19465634, 0]], dtype=np.float32),
    }
    rgb2lms = np.array([[0.3904725 , 0.54990437, 0.00890159],
                        [0.07092586, 0.96310739, 0.00135809],
                        [0.02314268, 0.12801221, 0.93605194]], dtype=np.float32)
    lms2rgb = np.array([[ 2.85831110e+00, -1.62870796e+00, -2.48186967e-02],
                        [-2.10434776e-01,  1.15841493e+00,  3.20463334e-04],
                        [-4.18895045e-02, -1.18154333e-01,  1.06888657e+00]], dtype=np.float32)
    
    lms = transform_colorspace(rgb, rgb2lms)
    sim_lms = transform_colorspace(lms, cb_matrices[color_deficit])
    sim_rgb = transform_colorspace(sim_lms, lms2rgb)
    return np.clip(sim_rgb, 0, 1)

def daltonize(rgb, color_deficit='d'):
    sim_rgb = simulate(rgb, color_deficit)
    err2mod = np.array([[0, 0, 0], [0.7, 1, 0], [0.7, 0, 1]], dtype=np.float32)
    err = transform_colorspace(rgb - sim_rgb, err2mod)
    dtpn = err + rgb
    return np.clip(dtpn, 0, 1)

# Gamma correction for sRGB
def gamma_correction(rgb, gamma=2.4):
    linear_rgb = np.zeros_like(rgb, dtype=np.float32)
    for i in range(3):
        mask = rgb[:, :, i] > 0.04045
        linear_rgb[mask, i] = ((rgb[mask, i] + 0.055) / 1.055) ** gamma
        linear_rgb[~mask, i] = rgb[~mask, i] / 12.92
    return linear_rgb

def inverse_gamma_correction(linear_rgb, gamma=2.4):
    rgb = np.zeros_like(linear_rgb, dtype=np.float32)
    for i in range(3):
        mask = linear_rgb[:, :, i] > 0.0031308
        rgb[mask, i] = 1.055 * (linear_rgb[mask, i] ** (1/gamma)) - 0.055
        rgb[~mask, i] = 12.92 * linear_rgb[~mask, i]
    return np.clip(rgb, 0, 1)

def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = gamma_correction(img)
    return img

def to_display_format(img):
    img = inverse_gamma_correction(img)
    img = (img * 255).astype(np.uint8)
    return img

if __name__ == "__main__":
    img_path = r"C:\Users\yasha\OneDrive\Pictures\Screenshots 1\Screenshot 2025-10-11 160813.png"
    img = load_image(img_path)

    sim_img = simulate(img, 'd')
    dalton_img = daltonize(img, 'd')
    sim_dalton_img = simulate(dalton_img, 'd')

    orig_disp = to_display_format(img)
    sim_disp = to_display_format(sim_img)
    dalton_disp = to_display_format(dalton_img)
    sim_dalton_disp = to_display_format(sim_dalton_img)

    titles = ['Original', 'Simulated Deuteranopia', 'Daltonized', 'Simulated Daltonized']
    images = [orig_disp, sim_disp, dalton_disp, sim_dalton_disp]

    import matplotlib.pyplot as plt
    plt.figure(figsize=(20, 5))
    for i, im in enumerate(images):
        plt.subplot(1, 4, i+1)
        plt.imshow(im)
        plt.title(titles[i])
        plt.axis('off')
    plt.tight_layout()
    plt.show()
