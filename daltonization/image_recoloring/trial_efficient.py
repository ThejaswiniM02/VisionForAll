import cv2
import numpy as np
import matplotlib.pyplot as plt
from daltonlens import simulate
from daltonlens import convert  

def load_image(path):
    im = cv2.imread(path)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

def simulate_cvd(im, deficiency='deutan', severity=1.0, model='Machado2009'):
    if model == 'Machado2009':
        sim = simulate.Simulator_Machado2009()
    elif model == 'Brettel1997':
        sim = simulate.Simulator_Brettel1997()
    elif model == 'Vienot1999':
        sim = simulate.Simulator_Vienot1999()
    else:
        raise ValueError("Unknown model")
    # Convert deficiency name to enum
    # e.g. 'deutan' → simulate.Deficiency.DEUTAN
    deficiency_enum = simulate.Deficiency[deficiency.upper()]
    return sim.simulate_cvd(im, deficiency=deficiency_enum, severity=severity)

# Simple fallback “correction” using error compensation (not full daltonization)
def simple_correct(im, cvd_simulated):
    # error = original - simulated
    err = im.astype(float) - cvd_simulated.astype(float)
    # attempt to add error back into channels that can help
    corrected = im.astype(float) + 0.7 * err
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)
    return corrected

# Optional contrast enhancement
def enhance_contrast(im):
    lab = cv2.cvtColor(im, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

# Full pipeline
def process_image(path, deficiency='deutan', severity=1.0, model='Machado2009'):
    orig = load_image(path)
    sim_orig = simulate_cvd(orig, deficiency, severity, model)
    corrected = simple_correct(orig, sim_orig)
    enhanced = enhance_contrast(corrected)
    sim_corrected = simulate_cvd(enhanced, deficiency, severity, model)
    return orig, sim_orig, corrected, enhanced, sim_corrected

# Display
def show_results(path, deficiency='deutan', severity=1.0, model='Machado2009'):
    orig, sim_orig, corr, enh, sim_corr = process_image(path, deficiency, severity, model)
    titles = [
        "Original",
        f"Simulated ({deficiency})",
        "Corrected (simple)",
        "Enhanced",
        f"Simulated Corrected ({deficiency})"
    ]
    imgs = [orig, sim_orig, corr, enh, sim_corr]
    plt.figure(figsize=(20, 8))
    for i, im in enumerate(imgs):
        plt.subplot(1, len(imgs), i+1)
        plt.imshow(im)
        plt.title(titles[i])
        plt.axis('off')
    plt.tight_layout()
    plt.savefig("daltonlens_fallback.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    img_path = r"C:\Users\yasha\Pictures\Screenshots\Screenshot 2025-10-11 160813.png"
    show_results(img_path, deficiency='deutan', severity=1.0, model='Machado2009')
