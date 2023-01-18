import numpy as np
import hashlib
import random

size = 420 #　Image Size
pixel = 70 #　Size of 1 pixel
frame = 35 #　Margin Size
background = 240 #　Background color (0-255)

def create_pattern(hash_value):
    pat = np.array([int(hash,16)%2 for hash in hash_value[:15]])
    pat = pat.reshape(3,5).T
    pat = np.append(pat[:,-1:0:-1], pat, axis=1)
    return pat

def create_color(hash_value):
    hue = ''
    for i in range(3): hue += hash_value[25+i]
    hue = int(hue,16) / 4095 * 360
    sat = ''
    for i in range(2): sat += hash_value[28+i]
    sat = 65 - int(sat,16) / 255 * 20
    lum = ''
    for i in range(2): lum += hash_value[30+i]
    lum = 75 - int(lum,16) / 255 * 20

    if lum < 50:
        max = 2.55 * (lum + lum * (sat/100))
        min = 2.55 * (lum - lum * (sat/100))
    elif lum >= 50:
        max = 2.55 * (lum + (100-lum) * (sat/100))
        min = 2.55 * (lum - (100-lum) * (sat/100))

    if 0 <= hue < 60:
        red   = max
        green = (hue/60) * (max-min) + min
        blue  = min
    elif 60 <= hue < 120:
        red   = ((120-hue)/60) * (max-min) + min
        green = max
        blue  = min
    elif 120 <= hue < 180:
        red   = min
        green = max
        blue  = ((hue-120)/60) * (max-min) + min
    elif 180 <= hue < 240:
        red   = min
        green = ((240-hue)/60) * (max-min) + min
        blue  = max
    elif 240 <= hue < 300:
        red   = ((hue-240)/60) * (max-min) + min
        green = min
        blue  = max
    elif 300 <= hue <= 360:
        red   = max
        green = min
        blue  = ((360-hue)/60) * (max-min) + min
    return [red,green,blue]

def create_image(pattern, colors):
    image = np.full([size,size,3],background)

    for i in range(5):
        for j in range(5):
                for k in range(pixel):
                    for l in range(pixel):
                        if pattern[i][j] == 0:
                            image[frame+i*pixel+k][frame+j*pixel+l][0] = colors[2]
                            image[frame+i*pixel+k][frame+j*pixel+l][1] = colors[1]
                            image[frame+i*pixel+k][frame+j*pixel+l][2] = colors[0]
                        elif pattern[i][j] == 1:
                            image[frame+i*pixel+k][frame+j*pixel+l][:] = background
    return image

def send_image():
    myid = str(random.randrange(10**7,10**8))
    hash_value = hashlib.md5(myid.encode()).hexdigest()
    pat = create_pattern(hash_value)
    colors = create_color(hash_value)
    image = create_image(pat, colors)
    return image