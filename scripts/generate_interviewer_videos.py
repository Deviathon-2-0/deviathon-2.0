import os
import math
import numpy as np
from PIL import Image, ImageFilter
import cv2
import imageio_ffmpeg
import asyncio
import edge_tts

INTERVIEWERS = {
    'kabir': {
        'mouth_y': 365,
        'mouth_x': 688,
        'mouth_w': 50,
        'eye_y': 246,
        'voice': 'en-IN-PrabhatNeural',
        'intro': "Hello! I am Kabir. Let's delve into your technical architecture and problem-solving strategy."
    },
    'payal': {
        'mouth_y': 343,
        'mouth_x': 688,
        'mouth_w': 46,
        'eye_y': 255,
        'voice': 'en-IN-NeerjaExpressiveNeural',
        'intro': "Hi there! I am Payal. I look forward to exploring your distributed systems and algorithmic trade-offs."
    },
    'charlotte': {
        'mouth_y': 330,
        'mouth_x': 688,
        'mouth_w': 45,
        'eye_y': 245,
        'voice': 'en-GB-SoniaNeural',
        'intro': "Good day. I am Charlotte. We shall explore system constraints, latency guarantees, and failure modes."
    },
    'john': {
        'mouth_y': 343,
        'mouth_x': 688,
        'mouth_w': 48,
        'eye_y': 250,
        'voice': 'en-US-ChristopherNeural',
        'intro': "Hey there! I am John. Excited to chat through your approach and see how you tackle scaling bottlenecks."
    },
    'sarah': {
        'mouth_y': 341,
        'mouth_x': 688,
        'mouth_w': 46,
        'eye_y': 252,
        'voice': 'en-US-JennyNeural',
        'intro': "Welcome. I am Sarah. Let's walk through your engineering background and architectural decisions."
    },
    'kenji': {
        'mouth_y': 330,
        'mouth_x': 688,
        'mouth_w': 45,
        'eye_y': 240,
        'voice': 'en-US-EricNeural',
        'intro': "Hello, I am Kenji. We will focus on data consensus, partitioning, and resilience today."
    }
}

OUT_DIR = "frontend/assets/interviewers"
TARGET_W = 1280
TARGET_H = 720
FPS = 30
DURATION = 4.0  # 4 seconds loop = 120 frames
TOTAL_FRAMES = int(FPS * DURATION)


def create_blink_overlay(img_arr, eye_y, eye_x=688, blink_factor=0.0):
    """Subtly blend upper eyelid downwards over eye socket."""
    if blink_factor <= 0.01:
        return img_arr
    res = img_arr.copy()
    h, w, _ = res.shape
    # Eye region box
    ey1, ey2 = max(0, eye_y - 25), min(h, eye_y + 25)
    ex1, ex2 = max(0, eye_x - 120), min(w, eye_x + 120)
    
    # Skin tone from brow region
    skin_sample = np.mean(res[max(0, eye_y - 20):max(0, eye_y - 10), ex1:ex2], axis=(0, 1))
    
    # Gaussian mask for both eyes
    y_idx, x_idx = np.ogrid[ey1:ey2, ex1:ex2]
    # Two eye centers: left at eye_x - 45, right at eye_x + 45
    d_left = ((x_idx - (eye_x - 48)) / 22)**2 + ((y_idx - eye_y) / 12)**2
    d_right = ((x_idx - (eye_x + 48)) / 22)**2 + ((y_idx - eye_y) / 12)**2
    
    mask_left = np.exp(-d_left)
    mask_right = np.exp(-d_right)
    mask = np.maximum(mask_left, mask_right) * blink_factor * 0.88
    mask = np.clip(mask, 0.0, 1.0)[:, :, np.newaxis]
    
    patch = res[ey1:ey2, ex1:ex2]
    eyelid = np.full_like(patch, skin_sample, dtype=np.uint8)
    res[ey1:ey2, ex1:ex2] = (patch * (1.0 - mask) + eyelid * mask).astype(np.uint8)
    return res


def create_talking_frame(base_img, mouth_y, mouth_x, mouth_w, open_amt, head_dy, head_rot, blink_amt, eye_y):
    """Renders a single frame with realistic lipsync opening and head micro-motion."""
    h_orig, w_orig = base_img.shape[:2]
    frame = base_img.copy()

    # 1. Mouth opening articulation (lipsync)
    if open_amt > 0.02:
        # Bounding box for lower face
        my1 = int(mouth_y - 15)
        my2 = int(mouth_y + 40)
        mx1 = int(mouth_x - mouth_w - 15)
        mx2 = int(mouth_x + mouth_w + 15)

        # Mouth interior: subtle shadow and teeth hint
        aperture_h = int(open_amt * 11)  # max 11px vertical opening
        if aperture_h > 0:
            # Shift lower lip and chin downwards
            chin_y1 = int(mouth_y + 2)
            chin_y2 = min(h_orig, int(mouth_y + 55))
            shift_px = int(open_amt * 7)
            
            # Warp lower lip region downward smoothly
            lower_patch = frame[chin_y1:chin_y2, mx1:mx2].copy()
            warped = cv2.resize(lower_patch, (lower_patch.shape[1], lower_patch.shape[0] + shift_px))
            frame[chin_y1 + shift_px:chin_y2 + shift_px, mx1:mx2] = warped[:chin_y2 - chin_y1, :]

            # Inner mouth dark cavity
            cavity_y1 = mouth_y - 1
            cavity_y2 = mouth_y + aperture_h
            cw = int(mouth_w * (0.65 + open_amt * 0.25))
            cx1 = mouth_x - cw
            cx2 = mouth_x + cw

            y_grid, x_grid = np.ogrid[cavity_y1:cavity_y2 + 2, cx1:cx2]
            rad_y = max(1, (cavity_y2 - cavity_y1) / 2.0)
            rad_x = cw * 1.0
            mid_y = (cavity_y1 + cavity_y2) / 2.0
            ellipse = ((x_grid - mouth_x) / rad_x)**2 + ((y_grid - mid_y) / rad_y)**2
            cavity_mask = np.clip(1.0 - ellipse, 0.0, 1.0)[:, :, np.newaxis]

            # Deep dark red / shadow for inner oral cavity
            inner_color = np.array([25, 12, 18], dtype=np.uint8)
            teeth_color = np.array([215, 205, 200], dtype=np.uint8)

            target_region = frame[cavity_y1:cavity_y2 + 2, cx1:cx2]
            if target_region.shape[0] == cavity_mask.shape[0] and target_region.shape[1] == cavity_mask.shape[1]:
                # Upper sliver of cavity has subtle teeth reflection
                cavity_layer = np.full_like(target_region, inner_color)
                if aperture_h >= 3:
                    teeth_rows = min(3, aperture_h // 2)
                    cavity_layer[:teeth_rows, int(cw*0.3):int(cw*1.7)] = teeth_color

                frame[cavity_y1:cavity_y2 + 2, cx1:cx2] = (
                    target_region * (1.0 - cavity_mask * 0.92) + cavity_layer * (cavity_mask * 0.92)
                ).astype(np.uint8)

    # 2. Eye blinking
    if blink_amt > 0.01:
        frame = create_blink_overlay(frame, eye_y, mouth_x, blink_amt)

    # 3. Head sway and subtle breathing rotation
    if abs(head_dy) > 0.01 or abs(head_rot) > 0.01:
        M = cv2.getRotationMatrix2D((mouth_x, mouth_y - 80), head_rot, 1.0)
        M[1, 2] += head_dy
        frame = cv2.warpAffine(frame, M, (w_orig, h_orig), borderMode=cv2.BORDER_REFLECT)

    # Resize to standard 1280x720 16:9 output
    if (w_orig, h_orig) != (TARGET_W, TARGET_H):
        frame = cv2.resize(frame, (TARGET_W, TARGET_H), interpolation=cv2.INTER_AREA)

    return frame


def generate_videos_for_interviewer(name, cfg):
    print(f"--- Generating Video Loops for {name.upper()} ---")
    src_path = os.path.join(OUT_DIR, f"{name}.jpg")
    img = Image.open(src_path).convert('RGB')
    base_arr = np.array(img)

    mouth_y = cfg['mouth_y']
    mouth_x = cfg['mouth_x']
    mouth_w = cfg['mouth_w']
    eye_y = cfg['eye_y']

    # 1. GENERATE LISTENING VIDEO
    listening_path = os.path.join(OUT_DIR, f"{name}_listening.mp4")
    writer_list = imageio_ffmpeg.write_frames(listening_path, (TARGET_W, TARGET_H), fps=FPS, codec='libx264')
    writer_list.send(None)

    for i in range(TOTAL_FRAMES):
        t = i / FPS
        # Slow calm breathing (period 4.0s)
        phase = 2 * math.pi * (t / DURATION)
        head_dy = 1.6 * math.sin(phase)
        head_rot = 0.25 * math.sin(phase * 0.5)

        # Attentive blink at t = 2.0s
        blink = 0.0
        if 1.90 <= t <= 2.15:
            blink_p = (t - 1.90) / 0.25
            blink = math.sin(blink_p * math.pi)

        # Attentive subtle nod at t = 3.2s
        if 3.0 <= t <= 3.5:
            nod_p = (t - 3.0) / 0.5
            head_dy += 2.2 * math.sin(nod_p * math.pi)

        frame = create_talking_frame(
            base_arr, mouth_y, mouth_x, mouth_w,
            open_amt=0.0, head_dy=head_dy, head_rot=head_rot,
            blink_amt=blink, eye_y=eye_y
        )
        writer_list.send(frame.tobytes())

    writer_list.close()
    print(f"Saved: {listening_path}")

    # 2. GENERATE TALKING VIDEO (Dynamic speech articulation & lipsync)
    talking_path = os.path.join(OUT_DIR, f"{name}_talking.mp4")
    writer_talk = imageio_ffmpeg.write_frames(talking_path, (TARGET_W, TARGET_H), fps=FPS, codec='libx264')
    writer_talk.send(None)

    # Phoneme rhythm: syllable cadence (~3.8 Hz) modulated by sentence stress
    for i in range(TOTAL_FRAMES):
        t = i / FPS
        phase = 2 * math.pi * (t / DURATION)

        # Rhythmic speech mouth opening (viseme envelope)
        syllable_phase = 2 * math.pi * 3.8 * t
        stress_envelope = 0.55 + 0.45 * math.sin(2 * math.pi * 0.9 * t)
        raw_mouth = (math.sin(syllable_phase) + 0.3 * math.sin(syllable_phase * 2.1))
        # Ensure smooth loop at boundary (t=0 and t=4)
        boundary_fade = math.sin(math.pi * (t / DURATION))
        open_amt = max(0.0, raw_mouth * stress_envelope * boundary_fade)
        open_amt = min(1.0, open_amt * 1.35)

        # Natural speaking head dynamics
        head_dy = 2.2 * math.sin(phase * 2.0) + (open_amt * 1.2)
        head_rot = 0.55 * math.sin(phase * 1.5)

        # Blinks during speaking (t = 1.2s and t = 3.4s)
        blink = 0.0
        if 1.10 <= t <= 1.32:
            blink_p = (t - 1.10) / 0.22
            blink = math.sin(blink_p * math.pi)
        elif 3.30 <= t <= 3.52:
            blink_p = (t - 3.30) / 0.22
            blink = math.sin(blink_p * math.pi)

        frame = create_talking_frame(
            base_arr, mouth_y, mouth_x, mouth_w,
            open_amt=open_amt, head_dy=head_dy, head_rot=head_rot,
            blink_amt=blink, eye_y=eye_y
        )
        writer_talk.send(frame.tobytes())

    writer_talk.close()
    print(f"Saved: {talking_path}")


async def generate_intro_audio(name, cfg):
    audio_path = os.path.join(OUT_DIR, f"{name}_intro.mp3")
    print(f"Generating voice intro for {name} ({cfg['voice']})...")
    communicate = edge_tts.Communicate(cfg['intro'], cfg['voice'])
    await communicate.save(audio_path)
    print(f"Saved audio: {audio_path}")


async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, cfg in INTERVIEWERS.items():
        generate_videos_for_interviewer(name, cfg)
        try:
            await generate_intro_audio(name, cfg)
        except Exception as e:
            print(f"TTS notice for {name}: {e}")

    print("\nALL 6 INTERVIEWER TALKING & LISTENING VIDEOS GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())

