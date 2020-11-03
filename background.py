import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image
import io
from rembg.bg import remove

def im_crop_center(img, w, h):
    img_width, img_height = img.size
    left, right = (img_width - w) / 2, (img_width + w) / 2
    top, bottom = (img_height - h) / 2, (img_height + h) / 2
    left, top = round(max(0, left)), round(max(0, top))
    right, bottom = round(min(img_width - 0, right)), round(min(img_height - 0, bottom))
    return img.crop((left, top, right, bottom))


def change_bg(img, bg_path):
    if type(img) is str:
        im = np.array(Image.open(img))
    else:
        im = np.array(Image.fromarray(img))
    if bg_path == "":
        return im
    foreground = remove(im)
    print(foreground.size)
    background = im_crop_center(Image.open(bg_path), foreground.size[0], foreground.size[1])
    background.paste(foreground, (0, 0), foreground)
    return background


if __name__ == "__main__":
    plt.imshow(change_bg("images/human.png"))
    plt.show()

    while True:
        pass
