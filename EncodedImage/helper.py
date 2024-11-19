import numpy as np
import random

def random_rect(width=320, height=240):
    """Create an image with 4 vertical rectangles with random colors."""
    # Define the size of each rectangle and the overall image
    rectangle_width = width // 4
    rectangle_height = height
    num_rectangles = 4
    image_width = width
    image_height = rectangle_height

    # Create an empty image array
    image = np.zeros((image_height, image_width, 3), dtype=np.uint8)

    # Fill each rectangle with a random color
    for i in range(num_rectangles):
        color = [random.randint(0, 255) for _ in range(3)]
        if i == num_rectangles-1:
            image[:, i*rectangle_width:width] = color
            break
        else:
            image[:, i*rectangle_width:(i+1)*rectangle_width] = color
        
    return image

def list_info(ml: list[float]) -> list[float | float]:
    avg = sum(ml) / len(ml)
    max_ = max(ml)
    min_ = min(ml)

    return [avg, max_, min_]

