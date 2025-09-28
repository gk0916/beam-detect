from ultralytics.data.converter import yolo_bbox2segment
import argparse

parse = argparse.ArgumentParser()
parse.add_argument('-m','--model',default='sam_b.pt')
parse.add_argument('-src-dir','--source')
parse.add_argument('-save-dir','--savedir',default=None)
args = parse.parse_args()

if __name__ == '__main__':
    print(f'src-dir===={args.source}')
    yolo_bbox2segment(sam_model=args.model,im_dir=args.source,save_dir=args.savedir)
