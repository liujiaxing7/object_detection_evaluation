from torch.utils.data import ConcatDataset
from .voc import VOCDataset


_DATASETS = {
    'Dataset': VOCDataset,
}


def get_args(root_dir,classes, dataset_name, target, transform, target_transform, is_train, factory):
    args = {'data_dir': root_dir, }
    args['classes'] = classes
    args['transform'] = transform
    args['target_transform'] = target_transform
    if factory == VOCDataset:
        args['keep_difficult'] = not is_train
        args['image_sets_file'] = dataset_name
        args['train'] = is_train
        args['target'] = target

    return  args

def build_dataset(dataset_list,classes, dataset_type, root_dir, target, transform=None, target_transform=None, is_train=True):
    assert len(dataset_list) > 0
    datasets = []
    for dataset_name in dataset_list:
        factory = _DATASETS[dataset_type]
        args = get_args(root_dir,classes, dataset_name, target, transform, target_transform, is_train, factory)

        dataset = factory(**args)
        datasets.append(dataset)
    # for testing, return a list of datasets
    if not is_train:
        return datasets
    dataset = datasets[0] # todo
    # if len(datasets) > 1:
    #     dataset = ConcatDataset(datasets)

    return dataset
