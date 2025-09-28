import argparse

import torch
import onnx
from onnx2pytorch import ConvertModel




parse = argparse.ArgumentParser()
parse.add_argument('model',help='onnx model file')
# parse.add_argument('-src-dir','--source')
# parse.add_argument('-save-dir','--savedir',default=None)
args = parse.parse_args()

model = args.model
onnx_model = onnx.load(model)
pytorch_model = ConvertModel(onnx_model)

import os

path_name = os.path.dirname(model)
file_name = os.path.basename(model).split('.')[0]
torch.save(pytorch_model.state_dict(), os.path.join(path_name,file_name+'.pt'))

