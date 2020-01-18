"""
Helper functions to help creating the training examples
with the UI
"""
import math
import os
import glob
import PIL
from PIL import Image, ImageDraw, ImageOps

WHITE_LIMIT = 238
IMG_HEIGHT = 40
IMG_WIDTH = 900
# there is some overlap between the 40px tall images of text lines
# and sometimes a letter f or g or y spills down to the next row's top
# so we have to disregard those pixelcolumns that have nonwhite stuff only
# at the top or bottom 
NOISE_PX_TOP = 12
NOISE_PX_BOTTOM = 6
WORD_GAP_MIN = 12


INPUT_DIR = "../preproc_img/"
OUTPUT_DIR = "../line_img/"

# open black and white / greyscale image of 901 x 1280 px
# the originals are from "whitelines" app, then
# uploaded to dropbox, editex with Pixlr to "web size": 901 x 1280
# and to "monochrome" (greyscale) 
# image = Image.open("../preproc_img/b_wl_smaller/20191004-211826.png") 
EXPECTED_WIDTH = 901
EXPECTED_HEIGTH = 1280

TOP_OFFSET = 64

LINE_HEIGHT = 34.4

EXTRA_OFFSET = 0

imgfiles = [f for f in glob.glob(INPUT_DIR + "*.png")]


def cut_one_image(filename):
    image = Image.open(filename)
    clean_filename = os.path.basename(filename)[:-4]  # cut the '.png' part
    total_width = image.size[0]
    total_height = image.size[1]
    assert total_height == EXPECTED_HEIGTH
    assert total_width == EXPECTED_WIDTH

    for line_id in range(33):
        if line_id == 9 or line_id == 12:
            EXTRA_OFFSET = 2
        elif line_id > 9 and line_id < 12:
            EXTRA_OFFSET = 4
        else:
            EXTRA_OFFSET = 0
        crop_upper = int(line_id * LINE_HEIGHT + TOP_OFFSET) - 2 + EXTRA_OFFSET
        crop_lower = int((line_id + 1) * LINE_HEIGHT + TOP_OFFSET) + 3 + EXTRA_OFFSET

        if crop_lower - crop_upper < 40:
            crop_lower += 1
        cropped_line = image.crop((
            0, crop_upper,
            900, crop_lower
        ))
        cropped_line.save(OUTPUT_DIR + clean_filename + "_L{}.png".format(line_id))


def convert_img_to_black_and_white(image):
    limiter_fn = lambda x : x if x > 230 else 0
    bw_image = image.convert('L').point(limiter_fn, mode='1')
    return bw_image    


def is_px_column_white_only(bw_image, x_pos):
    white_pixels_in_col = 0
    for y in range(NOISE_PX_TOP, IMG_HEIGHT - NOISE_PX_BOTTOM):
        px = bw_image.getpixel((x_pos, y))
        if px >= WHITE_LIMIT:
            white_pixels_in_col += 1
    return white_pixels_in_col == (IMG_HEIGHT - NOISE_PX_BOTTOM - NOISE_PX_TOP)


def skip_white_only_cols_from_left(bw_image, start_x_pos):
    # returns x position where the first non-white-only pixel column is
    for x in range(start_x_pos, IMG_WIDTH):
        is_col_wo = is_px_column_white_only(bw_image, x)
        if not is_col_wo:
            return x


def find_next_word(bw_image, start_x_pos):
    next_word_starts_at = skip_white_only_cols_from_left(bw_image, start_x_pos) 
    if not next_word_starts_at:
        return None
    x = next_word_starts_at
    while x < IMG_WIDTH:
        x += 1
        if is_px_column_white_only(bw_image, x):
            white_gap_begins = x
            # is this a word gap or just a small gap between letters?
            next_black = skip_white_only_cols_from_left(
                bw_image, white_gap_begins
            )
            if next_black:
                x = next_black
            if not next_black:
                # reached end of line
                return (next_word_starts_at, white_gap_begins - 1)
            diff = next_black - white_gap_begins
            if diff >= WORD_GAP_MIN:
                return (next_word_starts_at, white_gap_begins - 1)


def word_pos_finder(image, underline_in_img=False):
    w, h = image.size
    assert h == IMG_HEIGHT
    assert w >= IMG_WIDTH
    # converting image to black and white for easy detection of white gaps
    # between words
    bw_image = convert_img_to_black_and_white(image)
    if underline_in_img:
        out_image = image.copy()
        draw = ImageDraw.Draw(out_image)
    search_from_x = 0
    found_words_xmin_xmax = []
    maybe_word_coords = find_next_word(bw_image, search_from_x)
    while maybe_word_coords:
        found_words_xmin_xmax.append(maybe_word_coords)
        if maybe_word_coords:
            (w_x_min, w_x_max) = maybe_word_coords
            search_from_x = w_x_max + 2
            if underline_in_img:
                draw.line([(w_x_min, 32), (w_x_max, 32)])
        maybe_word_coords = find_next_word(bw_image, search_from_x)
    if underline_in_img:
        return (found_words_xmin_xmax, out_image)
    else:
        return found_words_xmin_xmax

def locate_words(image, text_typed_in):
    if not text_typed_in:
        print("WARNING")
        print("Please type in the text")
    words_entered = text_typed_in.split(" ")
    words_xmin_xmax_list = word_pos_finder(
        image
    )
    if len(words_xmin_xmax_list) != len(words_entered):
        print("WARNING")
        print(f"Num of words typed in: {len(words_entered)}")
        print(f"Num of words found in image: {len(words_xmin_xmax_list)}")
        return None
    else:
        return list(zip(words_entered, words_xmin_xmax_list))

def locate_chars(image, text_entered):
    # at first let's find the words
    list_words_with_pos = locate_words(image, text_entered)
    
    # we'll collect the result here: each element in the list will be a
    # pair (tuple) consisting of a character and a min-x-position and
    # a max-x-position
    # for example ('z', 123, 155)
    all_char_xmin_list = []
    if list_words_with_pos:
        for word, pos in list_words_with_pos:
            print(f"word: '{word}'  xmin/xmax positions: {pos}")
            # chars_and_x_coords = locate_chars_in_word_apprx(
            chars_and_x_coords = locate_chars_in_word_smarter(
                word, pos[0], pos[1]
            )
            print("smart found:")
            print(chars_and_x_coords)
            all_char_xmin_list = all_char_xmin_list + chars_and_x_coords
        return all_char_xmin_list
    else:
        return None


def count_chars_in_word(word_str, char_list):
    counter = 0
    for char in word_str:
        if char in char_list:
            counter += 1
    return counter


extra_thin_chars = [',', '.', '!', ':', ';']
extra_thin_ratio = 0.25
thin_chars = ['i', 'j', 'l', 'I', 't']
thin_ratio = 0.55
slightly_thin_chars = ['f']
slightly_thin_ratio = 0.75
wide_chars = [
    'm', 'w',
    'A', 'B', 'C', 'D', 'E', 'G', 'H', 'K', 'L', 'O', 'Q', 'R', 'S', 'X',
    'Z'
]
wide_ratio = 1.35
extra_wide_chars = ['W', 'M', 'N']
extra_wide_ratio = 1.6
all_special_width_chars = (
    extra_thin_chars + thin_chars + slightly_thin_chars +
    wide_chars + extra_wide_chars
)


def get_apprx_char_width(char, avg_normal_char_width):
    if char in extra_thin_chars:
        return avg_normal_char_width * extra_thin_ratio
    if char in thin_chars:
        return avg_normal_char_width * thin_ratio
    if char in slightly_thin_chars:
        return avg_normal_char_width * slightly_thin_ratio
    if char in wide_chars:
        return avg_normal_char_width * wide_ratio
    if char in extra_wide_chars:
        return avg_normal_char_width * extra_wide_ratio
    return avg_normal_char_width


def locate_chars_in_word_smarter(word_str, x_min, x_max):
    # Adjusting estimated character boundaries by their expected widths. 
    # Thinnest characters are: '.', ',', '!', 'j', 'i', 'l', somewhat 't', 'f'
    # and 'r'
    # Widest characters are: 'W', 'M', 'N', 'T', 'E', 'w', 'm'

    num_chars = len(word_str)
    # count how many we have in this word of the special width characters
    num_extra_thin_chars = count_chars_in_word(word_str, extra_thin_chars)
    num_thin_chars = count_chars_in_word(word_str, thin_chars)
    num_slightly_thin_chars = count_chars_in_word(
        word_str, slightly_thin_chars
    )
    num_wide_chars = count_chars_in_word(word_str, wide_chars)
    num_extra_wide_chars = count_chars_in_word(word_str, extra_wide_chars)

    # the rest are normal-width characters (ratio = 1.0)
    num_normal_chars = num_chars - count_chars_in_word(
        word_str, all_special_width_chars  
    )
    word_width = x_max - x_min + 1
    avg_normal_char_width = 1.0 * word_width / (
        num_normal_chars * 1.0 +
        num_extra_thin_chars * extra_thin_ratio +
        num_thin_chars * thin_ratio +
        num_slightly_thin_chars * slightly_thin_ratio +
        num_wide_chars * wide_ratio +
        num_extra_wide_chars * extra_wide_ratio
    )
    # Finally we can assign x_min positions to each character
    res = []
    x_tracker = x_min
    for char in word_str:
        cw = get_apprx_char_width(char, avg_normal_char_width)
        res.append((char, x_tracker, x_tracker + round(cw)))
        x_tracker += round(cw)
    return res


def test_word_pos_finder():
    img = Image.open("../test_data/20191004-211826_L7.png")
    coords, img_w_words = word_pos_finder(img, underline_in_img=True)
    img_w_words.show()

if __name__ == "__main__":
    # for f in imgfiles:
    #    cut_one_image(f)

    test_word_pos_finder()
