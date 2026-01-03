# Receives and validates frames from student client
# Converts base64 to image format for processing

import base64
import io
from PIL import Image
import numpy as np


def decode_frame(frame_data: str) -> np.ndarray:
    """
    Converts base64-encoded frame to numpy array (RGB format)
    Returns None if decoding fails
    """
    try:
        image_data = base64.b64decode(frame_data)
        image = Image.open(io.BytesIO(image_data))
        # Convert to RGB if needed (handles RGBA, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return np.array(image)
    except Exception as e:
        print(f"Frame decode error: {e}")
        return None


def validate_frame(frame_array: np.ndarray) -> bool:
    """
    Validates frame has valid dimensions and data
    """
    if frame_array is None:
        return False
    if len(frame_array.shape) != 3:
        return False
    if frame_array.shape[2] != 3:
        return False
    if frame_array.shape[0] < 100 or frame_array.shape[1] < 100:
        return False
    return True

