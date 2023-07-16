import cv2
import numpy as np
from skimage import img_as_ubyte
from skimage.metrics import structural_similarity as ssim

def image_from_bytes(image_bytes):
    """Load image from bytes"""
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, flags=cv2.IMREAD_COLOR)
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert image to grayscale

def get_phash(image):
    """Compute perceptual hash of an image"""
    resized = cv2.resize(image, (8, 8), interpolation = cv2.INTER_AREA)
    dct = cv2.dct(np.float32(resized))
    dct_low_freq = dct[:8, :8]
    avg_val = np.mean(dct_low_freq)
    phash = img_as_ubyte(dct_low_freq > avg_val)
    return phash

def compare_images(phash1, phash2):
    """Compute similarity between two image hashes"""
    return ssim(phash1, phash2)


def get_img(binary_images, new_image_bytes):

    # Convert new image bytes to cv2 image
    new_image = image_from_bytes(new_image_bytes)
    new_phash = get_phash(new_image)

    max_similarity = -1
    most_similar_image = None
    for img_bytes in binary_images:
        img = image_from_bytes(img_bytes)
        img_phash = get_phash(img)
        similarity = compare_images(new_phash, img_phash)
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_image = img_bytes
    return most_similar_image