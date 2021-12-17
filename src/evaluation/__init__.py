from src.voc import VOCDataset
# from .coco import evaluation as evaluationCoco
from .xml import evaluation as evaluationXml


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
        return evaluationXml(**args)
    # elif isinstance(dataset, COCODataset):
    #     return evaluationCoco(**args)
    # elif isinstance(dataset, ImageByXML):
    #     return evaluationXml(**args)
    else:
        raise NotImplementedError
