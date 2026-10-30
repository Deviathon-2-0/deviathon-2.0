from PIL import Image
import numpy as np

interviewers = ['kabir', 'payal', 'charlotte', 'john', 'sarah', 'kenji']

for name in interviewers:
    im = Image.open(f'frontend/assets/interviewers/{name}.jpg').convert('RGB')
    arr = np.array(im, dtype=np.float32)
    h, w, _ = arr.shape
    
    # Analyze central face column
    cx = w // 2
    x_min, x_max = int(cx - w * 0.08), int(cx + w * 0.08)
    y_min, y_max = int(h * 0.25), int(h * 0.70)
    
    crop = arr[y_min:y_max, x_min:x_max]
    
    # Red chrominance (lips usually stand out with R - (G+B)/2)
    redness = crop[:, :, 0] - (crop[:, :, 1] + crop[:, :, 2]) / 2.0
    
    # Find row with maximum redness in lower half (mouth)
    lower_half_offset = int(crop.shape[0] * 0.40)
    mouth_row = np.argmax(np.mean(redness[lower_half_offset:], axis=1)) + lower_half_offset + y_min
    
    # Eye line is in upper region where darkness of pupils/eyeballs/brows is present
    luminance = np.mean(crop[:lower_half_offset], axis=(1, 2))
    eye_row = np.argmin(luminance) + y_min
    
    print(f"{name}: mouth_y={mouth_row} ({mouth_row/h:.3f}), eye_y={eye_row} ({eye_row/h:.3f}), center_x={cx}")
