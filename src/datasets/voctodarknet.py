import os
import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join


def get_img(input_dir):
    xml_path_list = []
    for (root_path, dirname, filenames) in os.walk(input_dir):
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.png'):
                xml_path = root_path + "/" + filename
                xml_path_list.append(xml_path)
    return xml_path_list


def create_txt(file_path):
    xmlfilepath = os.path.join(file_path, "JPEGImages")
    output_path = os.path.join(file_path, "ImageSets/Main")
    total_xml = get_img(xmlfilepath)

    num = len(total_xml)
    # total_xml.sort()
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    trainval = open(output_path + '/trainval.txt', 'w')

    count1 = 0
    for i in range(num):
        name1 = total_xml[i][:-4] + '\n'
        name = name1.split('JPEGImages')[1]
        if i in range(num):
            trainval.write(name)
            count1 += 1


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


# 生成标签函数，从xml文件中提取有用信息写入txt文件
def convert_annotation(image_id, file_path, classes):
    in_file = open(file_path + '/Annotations/%s.xml' % (image_id))  # Annotations文件夹地址
    out_file = open(file_path + '/labels/%s.txt' % (image_id), 'w')  # labels文件夹地址
    if not os.path.exists(file_path + '/labels'):
        os.makedirs(file_path + '/labels')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


def voctodark(file_path, classes):
    create_txt(file_path)
    # image_ids = open(file_path+'/ImageSets/Main/trainval.txt').read().strip().split()
    # list_file = open(file_path+'/trainval.txt', 'w')
    #
    # for image_id in image_ids:
    #     # convert_annotation(image_id,file_path,classes)
    #     list_file.write(file_path+'/images/%s.jpg\n' % (image_id))
    # list_file.close()
