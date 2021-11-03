# import argparse
# import logging
# import os
#
#
# import onnx
#
# def main():
#     parser = argparse.ArgumentParser(description='Onnx Model Evaluation support VOC,COCO and Darknet dataset.')
#
#     parser.add_argument("--model_path",help="The path to the onnx model for test",default="./config/model/yolov3.onnx",type=str,)
#     parser.add_argument("--batchsize",help="The batchsize",default=128,type=int,)
#     parser.add_argument("--data_dir", default="/home/fandong/Code/Evaluation-procedure/datapig", type=str, help="The directory to store evaluation results.")
#     # parser.add_argument("--class_names", default=[], type=list, help="The classes of datasets.")
#     parser.add_argument("--data_format", default='darknet', type=str, choices=['voc','coco','darknet'])
#     parser.add_argument("--classes", default="./config/classes.names"
#                         , type=str, help="The directory to get the classes of datasets")
#
#     args = parser.parse_args()
#
#     num_gpus = int(os.environ["WORLD_SIZE"]) if "WORLD_SIZE" in os.environ else 1
#     distributed = num_gpus > 1
#
#     if torch.cuda.is_available():
#         # This flag allows you to enable the inbuilt cudnn auto-tuner to
#         # find the best algorithm to use for your hardware.
#         torch.backends.cudnn.benchmark = True
#     if distributed:
#         torch.cuda.set_device(args.local_rank)
#         torch.distributed.init_process_group(backend="nccl", init_method="env://")
#     evaluation=onnx.ONNX(args.model_path,args.batchsize,args.data_dir,args.classes,args.data_format)
#     evaluation.evaluate()
#
# if __name__ == '__main__':
#     main()
