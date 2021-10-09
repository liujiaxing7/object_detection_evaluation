
from .voc import VOCDataset


_DATASETS = {
    'Dataset': VOCDataset,
}


def get_args(root_dir,classes, target, transform, target_transform, is_train, factory,format):
    args = {'data_dir': root_dir, }
    args['classes'] = classes
    args['transform'] = transform
    args['target_transform'] = target_transform
    if factory == VOCDataset:
        args['keep_difficult'] = not is_train

        args['train'] = is_train
        args['target'] = target
        args['format']=format

    return  args

def build_dataset(classes, dataset_type, root_dir,format, target, transform=None, target_transform=None, is_train=True):

    factory = _DATASETS[dataset_type]
    args = get_args(root_dir,classes,  target, transform, target_transform, is_train, factory,format)

    dataset = factory(**args)


    return dataset
