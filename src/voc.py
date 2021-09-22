import os
from .xml import XML

class VOCDataset(XML):
    '''
    class_names = ('__background__',
               'aeroplane', 'bicycle', 'bird', 'boat',
               'bottle', 'bus', 'car', 'cat', 'chair',
               'cow', 'diningtable', 'dog', 'horse',
               'motorbike', 'person', 'pottedplant',
               'sheep', 'sofa', 'train', 'tvmonitor')
    '''
    # class_names = ('person', 'escalator', 'escalator_handrails', 'person_dummy', 'escalator_model', 'escalator_handrails_model')
    # class_names = ['person','person_dummy','person_model','escalator_handrails','escalator']

    def __init__(self, data_dir,classes, target, transform=None, target_transform=None, keep_difficult=False, train=False):
        """Dataset for VOC data.
        Args:
            data_dir: the root of the VOC2007 or VOC2012 dataset, the directory contains the following sub-directories:
                Annotations, ImageSets, JPEGImages, SegmentationClass, SegmentationObject.
        """
        # year, mode = image_sets_file.split('_')
        # data_dir = os.path.join(data_dir, year)
        image_sets_file = os.path.join(data_dir, "ImageSets", "Main", "trainval.txt" )

        super(VOCDataset, self).__init__(data_dir,classes, image_sets_file, target, transform, target_transform, keep_difficult, train)


    def get_file(self, index):
        image_id = self.file_list[index]
        image_file = self.data_dir+ "/JPEGImages"+ "%s.png" % image_id
        annotation_file = self.data_dir+ "/Annotations"+ "%s.xml" % image_id
        if not os.path.isfile(image_file):
            image_file = self.data_dir+ "/JPEGImages"+ "%s.jpg" % image_id
        # annotation_file = os.path.join(self.data_dir, "Annotations", "%s.xml" % image_id)
        return image_file, annotation_file

    def get_file_darknet(self, index):
        image_id = self.file_list[index]
        image_file = self.data_dir+ "/JPEGImages"+ "%s.png" % image_id
        if not os.path.isfile(image_file):
            image_file = self.data_dir+ "/JPEGImages"+ "%s.jpg" % image_id
        annotation_file = self.data_dir+ "/labels"+ "%s.txt" % image_id
        return image_file, annotation_file

    def get_classes(self):
        return self.class_names

    def get_file_json(self):
        json_file=os.path.join(self.data_dir,"train.json")
        return json_file