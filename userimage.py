import numpy as np
import hashlib
import random

size = 420
pixel = 70
frame = 35
background = 240


def create_pattern(hash_value):
    pattern = np.array([int(hash, 16) % 2 for hash in hash_value[:15]])
    pattern = pattern.reshape(3, 5).T
    pattern = np.append(pattern[:, -1:0:-1], pattern, axis=1)
    return pattern


def create_color(hash_value):
    hue = int(hash_value[25:28], 16) / 4095 * 360
    sat = 65 - int(hash_value[28:30], 16) / 255 * 20
    lum = 75 - int(hash_value[30:32], 16) / 255 * 20

    if lum < 50:
        max_val = 2.55 * (lum + lum * (sat / 100))
        min_val = 2.55 * (lum - lum * (sat / 100))
    else:
        max_val = 2.55 * (lum + (100 - lum) * (sat / 100))
        min_val = 2.55 * (lum - (100 - lum) * (sat / 100))

    hue_interval = hue / 60
    x = (max_val - min_val) * (1 - abs(hue_interval % 2 - 1))

    if 0 <= hue < 60:
        red, green, blue = max_val, x + min_val, min_val
    elif 60 <= hue < 120:
        red, green, blue = x + min_val, max_val, min_val
    elif 120 <= hue < 180:
        red, green, blue = min_val, max_val, x + min_val
    elif 180 <= hue < 240:
        red, green, blue = min_val, x + min_val, max_val
    elif 240 <= hue < 300:
        red, green, blue = x + min_val, min_val, max_val
    else:
        red, green, blue = max_val, min_val, x + min_val

    return [red, green, blue]


def create_image(pattern, colors):
    image = np.full([size, size, 3], background)

    for i in range(5):
        for j in range(5):
            for k in range(pixel):
                for l in range(pixel):
                    pixel_value = image[frame + i * pixel + k][frame + j * pixel + l]
                    if pattern[i][j] == 0:
                        pixel_value[0], pixel_value[1], pixel_value[2] = (
                            colors[2],
                            colors[1],
                            colors[0],
                        )
                    elif pattern[i][j] == 1:
                        pixel_value[:] = background
    return image


def send_image():
    myid = str(random.randrange(10**7, 10**8))
    hash_value = hashlib.md5(myid.encode()).hexdigest()
    pattern = create_pattern(hash_value)
    color = create_color(hash_value)
    image = create_image(pattern, color)
    return image
