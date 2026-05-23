import os
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT'] = '0'

# pyrefly: ignore [missing-import]
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    enable_mkldnn=False
)

result = ocr.ocr('test.jpg')

for line in result:
    print(line)
