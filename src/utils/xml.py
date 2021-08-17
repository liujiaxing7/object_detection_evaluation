#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: xml.py
@time: 2020/11/6 下午4:33
@desc: 
'''
#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: to_voc.py
@time: 2020/4/2 下午1:35
@desc: 
'''
import  os
from lxml import etree as ET
from xml.dom import minidom
from src.ssd.utils import MkdirSimple

def WriteXML(box_list, label_list, width, height, file, class_names):
    root = ET.Element("annotation")
    # root.set("version", "1.0")
    ET.SubElement(root, "folder").text = "none"
    ET.SubElement(root, "filename").text = "none"
    ET.SubElement(root, "source").text = "none"
    ET.SubElement(root, "owner").text = "indemind"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = "3"
    ET.SubElement(root, "segmented").text = "0"

    for box, label in zip(box_list, label_list):
        object = ET.SubElement(root, "object")
        ET.SubElement(object, "name").text = class_names[label]
        ET.SubElement(object, "pose").text = "Unspecified"
        ET.SubElement(object, "truncated").text = "0"
        ET.SubElement(object, "difficult").text = "0"
        bndbox = ET.SubElement(object, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(int(box[0]))
        ET.SubElement(bndbox, "ymin").text = str(int(box[1]))
        ET.SubElement(bndbox, "xmax").text = str(int(box[2]))
        ET.SubElement(bndbox, "ymax").text = str(int(box[3]))
    tree = ET.ElementTree(root)

    MkdirSimple(file)
    tree.write(file, encoding="UTF-8", xml_declaration=True)
    root = ET.parse(file)
    file_lines = minidom.parseString(ET.tostring(root, encoding="Utf-8")).toprettyxml(
        indent="\t")
    file_line = open(file, "w", encoding="utf-8")
    file_line.write(file_lines)
    file_line.close()