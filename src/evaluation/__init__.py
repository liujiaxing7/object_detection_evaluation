from src.voc import VOCDataset
# from .coco import evaluation as evaluation_coco
from .xml import evaluation as evaluation_xml


def evaluate(dataset, predictions, output_dir, save_anno, **kwargs):
    """evaluate dataset using different methods based on dataset type.
    Args:
        dataset: Dataset object
        predictions(list[(boxes, labels, scores)]): Each item in the list represents the
            prediction results for one image. And the index should match the dataset index.
        output_dir: output folder, to save evaluation files or results.
    Returns:
        evaluation result
    """
    args = dict(
        dataset=dataset, predictions=predictions, output_dir=output_dir, save_anno=save_anno, **kwargs,
    )
    if isinstance(dataset, VOCDataset):
        return evaluation_xml(**args)
    # elif isinstance(dataset, COCODataset):
    #     return evaluation_coco(**args)
    # elif isinstance(dataset, ImageByXML):
    #     return evaluation_xml(**args)
    else:
        raise NotImplementedError
