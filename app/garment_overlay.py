import cv2

def overlay_garment(frame, garment_img_path):
    try:
        overlay = cv2.imread(garment_img_path, cv2.IMREAD_UNCHANGED)
        if overlay is None:
            return frame

        overlay_resized = cv2.resize(overlay, (frame.shape[1], frame.shape[0]))

        # Blend with alpha channel if present
        if overlay_resized.shape[2] == 4:
            alpha = overlay_resized[:, :, 3] / 255.0
            for c in range(3):
                frame[:, :, c] = alpha * overlay_resized[:, :, c] + (1 - alpha) * frame[:, :, c]
        return frame
    except:
        return frame
