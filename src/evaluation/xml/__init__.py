import logging
import os
from datetime import datetime

import numpy as np
from pycocotools.coco import COCO
from src.database.db import DBManager
from .eval_detection import eval_detection_voc
BATCH_SIZE=10
def nan_str(p, space=True):
    if np.isnan(p):
        return "{:<5}".format(str(p)) if space else 0
    else:
        return "{:.3f}".format(p)
def nan_str_int(p, space=True):
    if np.isnan(p):
        return "{:<5}".format(str(p)) if space else 0
    else:
        return "{:d}".format(p)

def print_csv(result, class_names):
    prefix, flag = "", ','
    result_str = "\nmAP,recall,F1,Prediction\n"
    result_str += "{:.3f},{:.3f},{:.3f},{:.3f}\n".format(result["map"], np.nanmean(result['rec']), result['F1']
                                                                        ,np.nanmean(result['prec']))

    table_width = 12
    head_str = "{}{}".format("class_names".ljust(table_width), flag)
    AP_str = "{}{}".format("AP".ljust(table_width), flag)
    pred_str = "{}{}".format("Prediction".ljust(table_width), flag)
    count_str = "{}{}".format("count".ljust(table_width), flag)
    recall_str = "{}{}".format("recall".ljust(table_width), flag)
    F1_str = "{}{}".format("F1".ljust(table_width), flag)
    score_str = "{}{}".format("score".ljust(table_width), flag)
    tp_str = "{}{}".format("TP".ljust(table_width), flag)
    fp_str = "{}{}".format("FP".ljust(table_width), flag)
    fn_str = "{}{}".format("FN".ljust(table_width), flag)

    metrics = {'mAP': result["map"]}
    for i, ap in enumerate(result["ap"]):
        # if i == 0:  # skip background
        #     continue
        metrics[class_names[i]] = ap
        head_str += "{}{}{}".format(prefix, class_names[i], flag)
        count_str += "{}{}{}".format(prefix, result['num'][i], flag)
        AP_str += "{}{}{}".format(prefix, nan_str(ap, False), flag)
        pred_str += "{}{}{}".format(prefix, nan_str(result['prec'][i], False), flag)
        recall_str += "{}{}{}".format(prefix, nan_str(result['rec'][i], False), flag)
        F1_str += "{}{}{}".format(prefix, nan_str(result['f1'][i], False), flag)
        score_str += "{}{}{}".format(prefix, nan_str(result['threshold'][i], False), flag)
        tp_str += "{}{}{}".format(prefix, nan_str_int(result['tp'][i], False), flag)
        fp_str += "{}{}{}".format(prefix, nan_str_int(result['fp'][i], False), flag)
        fn_str += "{}{}{}".format(prefix, nan_str_int(result['fn'][i], False), flag)

    result_str += "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(head_str, count_str, AP_str, F1_str, pred_str, recall_str, score_str,tp_str,fp_str,fn_str)

    return result_str, metrics

def print_markdown(result, class_names):
    result_str = "\n| mAP   | recall | F1 | precision |\n"
    result_str += "| {:.3f} | {:.3f} | {:.3f} | {:.3f} |\n".format(result["map"], np.nanmean(result['rec']), 
                                                                   result['F1'], np.nanmean(result['prec']))

    table_width = 12
    head_str = "|{}|".format("class_names".ljust(table_width))
    AP_str = "|{}|".format("AP".ljust(table_width))
    pred_str = "|{}|".format("Prediction".ljust(table_width))
    count_str = "|{}|".format("count".ljust(table_width))
    recall_str = "|{}|".format("recall".ljust(table_width))
    F1_str = "|{}|".format("F1".ljust(table_width))
    score_str = "|{}|".format("score".ljust(table_width))

    metrics = {'mAP': result["map"]}
    for i, ap in enumerate(result["ap"]):
        # if i == 0:  # skip background
        #     continue
        metrics[class_names[i]] = ap
        space = " "
        if len(class_names[i]) > 7:
            head_str += "{:<15}|".format(class_names[i])
            space = "     "
        else:
            head_str += "{:<7}|".format(class_names[i])
        count_str += "{}{:<5}{}|".format(space, result['num'][i], space)
        AP_str += "{}{}{}|".format(space, nan_str(ap), space)
        pred_str += "{}{}{}|".format(space, nan_str(result['prec'][i]), space)
        recall_str += "{}{}{}|".format(space, nan_str(result['rec'][i]), space)
        F1_str += "{}{}{}|".format(space, nan_str(result['f1'][i]), space)
        score_str += "{}{}{}|".format(space, nan_str(result['threshold'][i]), space)

    result_str += "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(head_str, count_str, AP_str, F1_str, pred_str, recall_str, score_str)

    return result_str, metrics

def print_log(result, class_names):
    result_str = "\nmAP {:.3f} recall {:.3f} F1: {:.3f} \n".format(result["map"], np.nanmean(result['rec']), result['F1'])
    result_str += "{:<16}: {:<8} {:<6} {:<6} {:<6} {:<6}\n".format("class_names", "count", "ap", 'F1', "prediction", 'recall')

    metrics = {'mAP': result["map"]}
    for i, ap in enumerate(result["ap"]):
        # if i == 0:  # skip background
        #     continue
        metrics[class_names[i]] = ap
        result_str += "{:<16}: {:<8} {}  {}  {}  {}\n".format(class_names[i], result['num'][i],
                                                              nan_str(ap), nan_str(result['f1'][i]),
                                                              nan_str(result['prec'][i]), nan_str(result['rec'][i]))

    return result_str, metrics

def evaluation(dataset, predictions, output_dir, save_anno, iteration=None, threshold=None):

    class_names = dataset.get_classes()

    pred_boxes_list = []
    pred_labels_list = []
    pred_scores_list = []
    gt_boxes_list = []
    gt_labels_list = []
    gt_difficults = []

    for i in range(BATCH_SIZE):
        image_id, annotation = dataset.get_file(i)
        if not os.path.exists(annotation):
            continue
        gt_boxes, gt_labels = dataset.get_annotation(annotation)
        gt_boxes_list.append(gt_boxes)
        gt_labels_list.append(gt_labels)

        img_info = dataset.get_img_info(i)
        prediction = predictions[i]
        # prediction = prediction.resize((img_info['width'], img_info['height'])).numpy()
        boxes, labels, scores = prediction['boxes'], prediction['labels'], prediction['scores']

        pred_boxes_list.append(boxes)
        pred_labels_list.append(labels)
        pred_scores_list.append(scores)
    result = eval_detection_voc(pred_bboxes=pred_boxes_list,
                                pred_labels=pred_labels_list,
                                pred_scores=pred_scores_list,
                                gt_bboxes=gt_boxes_list,
                                gt_labels=gt_labels_list,
                                class_num=len(class_names),
                                iou_thresh=0.5,
                                use_07_metric=False,
                                threshold=threshold)
    if save_anno:
        print("writing xml")
        dataset.save_annotation(pred_boxes_list, pred_labels_list, pred_scores_list, result['threshold'], os.path.join(output_dir, 'xml'))
    for l in dataset.ignore:
        id = dataset.class_dict[l]
        for key in result.keys():
            if key != 'num':
                result[key][id] = np.nan
    result['F1'] = np.nanmean(result['f1'])
    result['map'] = np.nanmean(result['ap'])
    logger = logging.getLogger("SSD.inference")
    result_markdown, metrics = print_markdown(result, class_names)
    result_log, metrics = print_log(result, class_names)
    result_csv, _ = print_csv(result, class_names)
    result_str = result_markdown + '\n' + result_log
    logger.info(result_markdown)
    print(result_str)

    if iteration is not None:
        result_path = output_dir+'/result_{:07d}.txt'.format(iteration)
    else:
        result_path = output_dir+'/result_{}.txt'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    with open(result_path, "w") as f:
        f.write(result_str)
    with open(result_path.replace(".txt", ".csv"), "w") as f:
        f.write(result_csv)
    return result_csv

def evaluation_darknet(dataset, predictions, output_dir,save_anno, iteration=None, threshold=None):
    class_names = dataset.get_classes()

    pred_boxes_list = []
    pred_labels_list = []
    pred_scores_list = []
    gt_boxes_list = []
    gt_labels_list = []
    gt_difficults = []

    for i in range(BATCH_SIZE):
        image_id, annotation = dataset.get_file_darknet(i)
        if not os.path.exists(annotation):
            continue
        gt_boxes, gt_labels = dataset.get_darknet_labels(annotation)
        gt_boxes_list.append(gt_boxes)
        gt_labels_list.append(gt_labels)

        img_info = dataset.get_img_info(i)
        prediction = predictions[i]
        # prediction = prediction.resize((img_info['width'], img_info['height'])).numpy()
        boxes, labels, scores = prediction['boxes'], prediction['labels'], prediction['scores']

        pred_boxes_list.append(boxes)
        pred_labels_list.append(labels)
        pred_scores_list.append(scores)
    result = eval_detection_voc(pred_bboxes=pred_boxes_list,
                                pred_labels=pred_labels_list,
                                pred_scores=pred_scores_list,
                                gt_bboxes=gt_boxes_list,
                                gt_labels=gt_labels_list,
                                class_num=len(class_names),
                                iou_thresh=0.5,
                                use_07_metric=False,
                                threshold=threshold)
    if save_anno:
        print("writing xml")
        dataset.save_annotation(pred_boxes_list, pred_labels_list, pred_scores_list, result['threshold'], os.path.join(output_dir, 'xml'))
    for l in dataset.ignore:
        id = dataset.class_dict[l]
        for key in result.keys():
            if key != 'num':
                result[key][id] = np.nan
    result['F1'] = np.nanmean(result['f1'])
    result['map'] = np.nanmean(result['ap'])
    logger = logging.getLogger("SSD.inference")
    result_markdown, metrics = print_markdown(result, class_names)
    result_log, metrics = print_log(result, class_names)
    result_csv, _ = print_csv(result, class_names)
    result_str = result_markdown + '\n' + result_log
    logger.info(result_markdown)
    print(result_str)

    if iteration is not None:
        result_path = os.path.join(output_dir, '/result_{:07d}.txt'.format(iteration))
    else:
        result_path = os.path.join(output_dir, '/result_{}.txt'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
    with open(result_path, "w") as f:
        f.write(result_str)
    with open(result_path.replace(".txt", ".csv"), "w") as f:
        f.write(result_csv)

    return result_csv

def evaluation_coco(dataset, predictions, output_dir, save_anno, iteration=None, threshold=None):
    class_names = dataset.get_classes()

    pred_boxes_list = []
    pred_labels_list = []
    pred_scores_list = []
    gt_boxes_list = []
    gt_labels_list = []
    gt_difficults = []
    annotation_file=dataset.get_file_json()
    ann_file=COCO(annotation_file=annotation_file)
    for i in range(BATCH_SIZE):
        image_id, annotation = dataset.get_file_darknet(i)
        if not os.path.exists(annotation):
            continue
        gt_boxes, gt_labels = dataset.get_coco_labels(ann_file,image_id)
        gt_boxes_list.append(gt_boxes)
        gt_labels_list.append(gt_labels)


        img_info = dataset.get_img_info(i)
        prediction = predictions[i]
        # prediction = prediction.resize((img_info['width'], img_info['height'])).numpy()
        boxes, labels, scores = prediction['boxes'], prediction['labels'], prediction['scores']

        pred_boxes_list.append(boxes)
        pred_labels_list.append(labels)
        pred_scores_list.append(scores)
    result = eval_detection_voc(pred_bboxes=pred_boxes_list,
                                pred_labels=pred_labels_list,
                                pred_scores=pred_scores_list,
                                gt_bboxes=gt_boxes_list,
                                gt_labels=gt_labels_list,
                                class_num=len(class_names),
                                iou_thresh=0.5,
                                use_07_metric=False,
                                threshold=threshold)
    if save_anno:
        print("writing xml")
        dataset.save_annotation(pred_boxes_list, pred_labels_list, pred_scores_list, result['threshold'], os.path.join(output_dir, 'xml'))
    for l in dataset.ignore:
        id = dataset.class_dict[l]
        for key in result.keys():
            if key != 'num':
                result[key][id] = np.nan
    result['F1'] = np.nanmean(result['f1'])
    result['map'] = np.nanmean(result['ap'])
    logger = logging.getLogger("SSD.inference")
    result_markdown, metrics = print_markdown(result, class_names)
    result_log, metrics = print_log(result, class_names)
    result_csv, _ = print_csv(result, class_names)
    result_str = result_markdown + '\n' + result_log
    logger.info(result_markdown)
    print(result_str)

    if iteration is not None:
        result_path = os.path.join(output_dir, '/result_{:07d}.txt'.format(iteration))
    else:
        result_path = os.path.join(output_dir, '/result_{}.txt'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
    with open(result_path, "w") as f:
        f.write(result_str)
    with open(result_path.replace(".txt", ".csv"), "w") as f:
        f.write(result_csv)

    return result_csv
