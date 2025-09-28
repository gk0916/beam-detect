# import cv2
from pyzbar import pyzbar
from PIL import Image


def detect_qc(self,image_file):
    image = Image.open(image_file)

    barcodes = pyzbar.decode(image)

    res = []
    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        print("Barcode Type: {}, Barcode Data: {}".format(barcode_type, barcode_data))
        res.append((barcode_data,barcode_type))
    res
