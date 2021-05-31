from PIL import Image
import os

video_name = input("video name: ")
fps = 23.980458527730313
file_format = "jpg"


class termcolor:
    OKGREEN = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


class braille_config:
    # 2 * 3 braille
    base = 0x2800
    width = 2
    height = 3


class video_config:
    width = 192
    height = 82


def resize(image: Image.Image, width: int, height: int) -> Image.Image:
    if height == 0:
        height = int(im.height / im.width * width)
    if height % braille_config.height != 0:
        height = int(braille_config.height * (height // braille_config.height))
    if width % braille_config.width != 0:
        width = int(braille_config.width * (width // braille_config.width))
    return image.resize((width, height))


def convert_timedelta_to_srt_format(delta_in_ms: float, framecount: int):
    time = delta_in_ms * framecount
    hours = int(time // 3600000)
    minutes = int((time % 3600000) // 60000)
    seconds = int((time % 60000) // 1000)
    ms = int(time % 1000)
    return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, ms)


hex_threshold = 128
frames_folder = sorted(os.listdir(os.getcwd() + "/frames/" + video_name))
one_frame_in_ms = 1000.0 / fps

for idx in range(len(frames_folder)):
    normalized_path = os.path.abspath(
        f"{os.getcwd()}/frames/{video_name}/f{idx}.{file_format}"
    )
    im = Image.open(normalized_path)

    # (image, weight, height). 0 as height means auto
    resized_image = resize(im, video_config.width, video_config.height)
    resized_image_bw = resized_image.convert("1")  # apply dithering

    px = resized_image.load()
    pxbw = resized_image_bw.load()
    terminal_string = f"{idx + 1}\n"
    srt_string = f"{idx + 1}\n"
    srt_string += f"{convert_timedelta_to_srt_format(one_frame_in_ms, idx)} --> {convert_timedelta_to_srt_format(one_frame_in_ms, idx + 1)}\n"

    for h in range(0, resized_image.height, braille_config.height):
        for w in range(0, resized_image.width, braille_config.width):
            braille = [False] * braille_config.width * braille_config.height
            braille_r = 0
            braille_g = 0
            braille_b = 0
            for local_w in range(braille_config.width):
                for local_h in range(braille_config.height):
                    r, g, b, *rest = px[w + local_w, h + local_h]  # ignore alpha
                    bw = pxbw[w + local_w, h + local_h]  # dithered version
                    braille_r += r
                    braille_g += g
                    braille_b += b
                    if bw > hex_threshold:  # use dithered version of pixels
                        braille[local_w * braille_config.height + local_h] = True
            output = braille_config.base
            for b_idx, val in enumerate(braille):
                if val:
                    output += 2 ** b_idx
            braille_r //= braille_config.width * braille_config.height
            braille_g //= braille_config.width * braille_config.height
            braille_b //= braille_config.width * braille_config.height
            # terminal_string += "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(
            #     braille_r, braille_g, braille_b, chr(output)
            # )
            hex_color = "#%02X%02X%02X" % (braille_r, braille_g, braille_b)
            srt_string += f'<font color="#{hex_color}">' + chr(output) + "</font>"
        srt_string += "\n"
    with open(f"{video_name}.srt", "a", encoding="UTF-8") as file:
        file.write(srt_string + "\n")
    print(terminal_string)
