from ultralytics.data.annotator import auto_annotate
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-in', '--input', help='待标记图片路径')
parser.add_argument('-m', '--model', help='目标检测模型路径')
parser.add_argument('-sm', '--seg_model', help='分割模型路径')
parser.add_argument('-out', '--output', help='标签保存路径')
args = parser.parse_args()

auto_annotate(
    data=args.input,
    det_model=args.model,
    sam_model=args.seg_model,
    device="cuda",
    output_dir=args.output,
)