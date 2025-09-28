from ultralytics import YOLO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('pt_model_path')
parser.add_argument('-onnx','--onnx_model_path')
args = parser.parse_args()

model = YOLO(args.pt_model_path)
model.export(format='onnx', dynamic=True)