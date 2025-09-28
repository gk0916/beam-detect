from ultralytics import YOLO
import argparse
import wandb
from wandb.integration.ultralytics import add_wandb_callback
import os

os.environ["WANDB_MODE"] = "online"
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"



parser = argparse.ArgumentParser()
parser.add_argument('model', help='model file')
parser.add_argument('project', help='project name')
parser.add_argument('name', help='name')
parser.add_argument('data', help='yaml file for data')
parser.add_argument('-d', '--device', default=None, help='device')
parser.add_argument('-e','--epochs', default=10, type=int)
parser.add_argument('-i', '--iterations', default=1, type=int)
parser.add_argument('-o', '--optimizer', default='AdamW') # AdamW
parser.add_argument('-t', '--tune', default=False)
parser.add_argument('-r', '--use_ray', default=False)
parser.add_argument('-p', '--patience', default=100,type=int)
parser.add_argument('-dr', '--dropout', default=0.0,type=float)

args = parser.parse_args()


 
if __name__ == '__main__':

    # '''
    #   python train\train.py train\models\yolov8n.pt test-project test-train dataset\beams-dev\data.yaml -d 0 -e 10 -i 5 -t tune -r True -p 70 -dr 0.3
    # '''

    # 加载模型
    # model = YOLO("yolov8n.yaml")  # 从头开始构建新模型
    model = YOLO(args.model)  # 加载预训练模型（推荐用于训练）

    # Initialize a Weights & Biases run
    wandb.init(project=args.project, job_type="training")
    # Add W&B Callback for Ultralytics
    add_wandb_callback(model, enable_model_checkpointing=True)
    
    if not args.tune:
        print("model training......")
        # 训练模型
        model.train(project=args.project
                            , name=args.name
                            , data=args.data
                            , device=args.device
                            , epochs=args.epochs
                            , imgsz=(640,640)
                            , exist_ok=True
                            , batch=-1
                            , save_period=10
                            , save=True
                            , verbose=True
                            , lr0 = 0.01
                            , lrf = 0.01
                            , momentum = 0.937
                            , weight_decay = 0.0005
                            , warmup_epochs = 3.0
                            , warmup_momentum = 0.8
                            , box = 7.5
                            , cls = 0.5
                            , dfl = 1.5
                            , hsv_h = 0.015
                            , hsv_s = 0.7
                            , hsv_v = 0.4
                            , degrees = 0.0
                            , translate = 0.1
                            , scale = 0.5
                            , shear = 0.0
                            , perspective = 0.0
                            , flipud = 0.0
                            , fliplr = 0.5
                            , bgr = 0.0
                            , mosaic = 1.0
                            , mixup = 0.0
                            , cutmix = 0.0
                            , copy_paste = 0.0
                            )  
        # model.val(split='test')
    else:
        print("model tuning......")
        model.tune(data=args.data
                , epochs=args.epochs
                , iterations=args.iterations
                , optimizer=args.optimizer
                # , use_ray=args.use_ray
                , patience=args.patience
                , dropout=args.dropout
                )



# # Finalize the W&B Run
wandb.finish()