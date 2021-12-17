import numpy as np


def maxPool2d(feature_map, size, padding, stride=1):
    feature_map = np.squeeze(feature_map, axis=0)
    channel = feature_map.shape[0]
    height = feature_map.shape[1]
    width = feature_map.shape[2]
    padding_height = np.uint16(round((height - size + 1 + 2 * padding) / stride))
    padding_width = np.uint16(round((width - size + 1 + 2 * padding) / stride))

    pool_out = np.zeros((channel, padding_height, padding_width), dtype=np.float64)

    feature_map = np.pad(feature_map, ((0, 0), (padding, padding), (padding, padding)))

    for map_num in range(channel):
        out_height = 0
        for r in np.arange(0, height, stride):
            out_width = 0
            for c in np.arange(0, width, stride):
                pool_out[map_num, out_height, out_width] = np.max(feature_map[map_num, r:r + size, c:c + size])
                out_width = out_width + 1
            out_height = out_height + 1

    return pool_out


def centernetNms(heat, kernel=3):
    pad = (kernel - 1) // 2

    hmax = maxPool2d(heat, kernel, padding=pad, stride=1).astype(np.float32)
    keep = (hmax == heat)

    return heat * keep

def ssdNms(boxes, scores, nms_thresh):
    """ Performs non-maximum suppression using numpy
        Args:
            boxes(numpy): `xyxy` mode boxes, use absolute coordinates(not support relative coordinates),
                shape is (n, 4)
            scores(Tensor): scores, shape is (n, )
            nms_thresh(float): thresh
        Returns:
            indices kept.
    """
    # if boxes.numel() == 0:
    #     return np.empty((0,), dtype=np.long)
    # Use numpy to run nms. Running nms in PyTorch code on CPU is really slow.
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = np.argsort(scores)[::-1]
    num_detections = boxes.shape[0]
    suppressed = np.zeros((num_detections,), dtype=np.bool)
    for _i in range(num_detections):
        i = order[_i]
        if suppressed[i]:
            continue
        ix1 = x1[i]
        iy1 = y1[i]
        ix2 = x2[i]
        iy2 = y2[i]
        iarea = areas[i]

        for _j in range(_i + 1, num_detections):
            j = order[_j]
            if suppressed[j]:
                continue

            xx1 = max(ix1, x1[j])
            yy1 = max(iy1, y1[j])
            xx2 = min(ix2, x2[j])
            yy2 = min(iy2, y2[j])
            w = max(0, xx2 - xx1)
            h = max(0, yy2 - yy1)

            inter = w * h
            ovr = inter / (iarea + areas[j] - inter)
            if ovr >= nms_thresh:
                suppressed[j] = True
    keep = np.nonzero(suppressed == 0)[0]
    return keep
