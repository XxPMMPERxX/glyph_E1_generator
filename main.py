import codecs
from glob import glob
import os
import cv2
from urllib.request import urlopen
import numpy as np


TAG_INFO = '[INFO] '
TAG_ERROR = '[ERROR] '
BASE_PNG_URL = 'https://github.com/Nnse/Unicode-Bedrock-New/raw/main/font/glyph_E1_empty.png'
RESULT_PNG_PATH = '/glyph_E1.png'
RESULT_DICT_PATH = '/pictogram.ini'
ICONS_DIRECTORY_PATH = './icons'
DEST_DIRECTORY_PATH = './dest'
UNDEFINED_POSITIONS = [33, 34, 35, 36, 37, 38, 39, 40, 105, 114, 115, 116, 117, 118, 119, 120, 121, 136]
DATA_NAME_SEPARATOR = '#'
UNICODES = [
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '_', '_', '_', '_', '_', '_', '_', '_', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '_', '', '', '', '', '', '', '', '',
    '', '_', '_', '_', '_', '_', '_', '_', '_', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '_', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
]

class EntryImageFactory:
    __images: list[cv2.Mat]
    __names: list[str]

    def __init__(self):
        self.__images = []
        self.__names = []
        image_paths = glob(ICONS_DIRECTORY_PATH + '/*')
        for image_path in image_paths:
            if '.png' not in image_path:
                continue
            file_name = ((image_path.replace('\\', '/')).split('/')[-1]).split('.png')[0]
            if DATA_NAME_SEPARATOR in file_name:
                file_name = file_name.split(DATA_NAME_SEPARATOR)[-1]
            self.__images.insert(0, cv2.imread(image_path, -1))
            self.__names.insert(0, file_name)

    def get_images(self) -> list[cv2.Mat]:
        return self.__images

    def get_names(self) -> list[str]:
        return self.__names


# 画像のリサイズ
def resize_to_16x16(image: cv2.Mat) -> cv2.Mat:
    height = image.shape[0]
    width = image.shape[1]
    if height == width & height == 16:
        return image
    return cv2.resize(image, dsize=(16, 16), interpolation=cv2.INTER_NEAREST)


# URLから画像取得
def url_read(url: str, flags=cv2.IMREAD_UNCHANGED):
    response = urlopen(url)
    img = np.asarray(bytearray(response.read()), dtype=np.uint8)
    return cv2.imdecode(img, flags)


# ------------- ここから処理 -------------

# 例外処理
if not os.path.exists(ICONS_DIRECTORY_PATH):
    os.mkdir(ICONS_DIRECTORY_PATH)
    print(TAG_INFO + 'Please add all images to ' + ICONS_DIRECTORY_PATH)
    exit(1)
if not os.path.exists(DEST_DIRECTORY_PATH):
    os.mkdir(DEST_DIRECTORY_PATH)

# 画像登録処理
eif = EntryImageFactory()

# 取得
entries = eif.get_images()
names = eif.get_names()

# 何もなかったら処理終了
if len(entries) == 0:
    print(TAG_ERROR + 'No images in ' + ICONS_DIRECTORY_PATH)
    exit(1)

# ベースの256x256透過PNG取得
base = url_read(BASE_PNG_URL)

dictionary: list[str, str] = []
x_offset = 0
y_offset = 0
icon_num = 0
for i in range(16):
    y_offset = i * 16
    for j in range(16):
        x_offset = j * 16
        if len(entries) == 0:
            break
        icon_num += 1
        if icon_num in UNDEFINED_POSITIONS:
            continue
        name = names.pop()
        icon = entries.pop()

        # 1:1比率じゃなかったら飛ばす
        if not icon.shape[0] == icon.shape[1]:
            continue

        # サイズ調整
        icon = resize_to_16x16(icon)

        # アイコン画像の書き込み
        base[
            y_offset:y_offset + icon.shape[0],
            x_offset:x_offset + icon.shape[1]
        ] = icon

        # 名前の辞書登録
        dictionary.append(name + '=' + UNICODES[icon_num - 1] + '\r\n')

# 画像生成
cv2.imwrite(DEST_DIRECTORY_PATH + RESULT_PNG_PATH, base)

# 辞書作成
with codecs.open(DEST_DIRECTORY_PATH + RESULT_DICT_PATH, 'w', 'utf8') as f:
    f.writelines(dictionary)

print(TAG_INFO + 'All processes have been successful.')

exit(0)
