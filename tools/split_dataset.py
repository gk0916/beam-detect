from ultralytics.data.utils import autosplit
import argparse

autosplit( 
    path="path/to/images",
    weights=(0.9, 0.1, 0.0), # (train, validation, test) fractional splits
    annotated_only=False     # split only images with annotation file when True
)

parse = argparse.ArgumentParser()
parse.add_argument('source',help='dataset path')
parse.add_argument('--train',type=float, default=0.7, help='train dataset ratio')
parse.add_argument('--valid',type=float, default=0.2, help='valid dataset ratio')
parse.add_argument('--test',type=float, default=0.1, help='test dataset ratio')
args = parse.parse_args()

if __name__ == '__main__':
    autosplit(path=args.source,weights=(args.train,args.valid,args.test))