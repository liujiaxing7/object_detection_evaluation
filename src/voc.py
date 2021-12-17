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

    def __init__(self, data_dir, classes, target, transform=None, target_transform=None, keep_difficult=False,
                 train=False, format=None):
        """Dataset for VOC data.
        Args:
            data_dir: the root of the VOC2007 or VOC2012 dataset, the directory contains the following sub-directories:
                Annotations, ImageSets, JPEGImages, SegmentationClass, SegmentationObject.
        """
        # year, mode = image_sets_file.split('_')
        # data_dir = os.path.join(data_dir, year)
        # if self.format == 'darknet':
        #     batch_size=len(open(os.path.join(self.data_dir,  "val_images.txt" )).readlines())
        # else:
        #     batch_size=len(open(os.path.join(self.data_dir,  "JPEGImages","Main","test.txt" )).readlines())
        if format == 'darknet':
            image_sets_file = os.path.join(data_dir, "val_images.txt")
        else:
            image_sets_file = os.path.join(data_dir, "ImageSets", "Main", "test.txt")

        super(VOCDataset, self).__init__(data_dir, classes, image_sets_file, target, transform, target_transform,
                                         keep_difficult, train, format)

    def getFile(self, index):
        image_id = self.file_list[index]
        image_file = self.data_dir + "/JPEGImages/" + "%s.png" % image_id
        annotation_file = self.data_dir + "/Annotations/" + "%s.xml" % image_id
        if not os.path.isfile(image_file):
            image_file = self.data_dir + "/JPEGImages/" + "%s.jpg" % image_id
        # annotation_file = os.path.join(self.data_dir, "Annotations", "%s.xml" % image_id)
        return image_file, annotation_file

    def getFileTxt(self, index):
        image_id = self.file_list[index]
        image_file = image_id
        if 'JPEGImages' in image_id:
            annotation_file = image_id.replace('JPEGImages', 'Annotations').replace(os.path.splitext(image_id)[-1],
                                                                                    '.xml')
        else:

            annotation_file = image_id.replace('image', 'Annotations').replace(os.path.splitext(image_id)[-1], '.xml')

        return image_file, annotation_file

    def getFileTxtDarknet(self, index):
        image_id = self.file_list[index]
        image_file = image_id
        if 'JPEGImages' in image_id:
            annotation_file = image_id.replace('JPEGImages', 'labels').replace(os.path.splitext(image_id)[-1], '.txt')
        else:
            annotation_file = image_id.replace('image', 'labels').replace(os.path.splitext(image_id)[-1], '.txt')

        return image_file, annotation_file

    def getFileDarknet(self, index):
        image_id = self.file_list[index]
        image_file = self.data_dir + "/JPEGImages" + "%s.png" % image_id
        if not os.path.isfile(image_file):
            image_file = self.data_dir + "/JPEGImages" + "%s.jpg" % image_id
        annotation_file = self.data_dir + "/labels" + "%s.txt" % image_id
        return image_file, annotation_file

    def getClasses(self):
        return self.class_names

    def getFileJson(self):
        json_file = os.path.join(self.data_dir, "train.json")
        return json_file
