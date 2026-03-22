from typing import Union

import cupy
import cupyx.scipy.ndimage
import numpy as np
import scipy.ndimage
import skimage


def fill_holes_in_mask(
    mask: np.ndarray,
    compartment: Union[str, None] = None,
) -> np.ndarray:
    """
    This function fills holes in instance segmented mask images

    Parameters
    ----------
    mask : np.ndarray
        3D instance segmented mask image where each object has a unique integer label and background is 0
    compartment : str, optional
        Compartment type of the mask (e.g. "cell" or "organoid"), by default None. This is used to determine the hole filling strategy.

    Errors
    ------
    ValueError
        If compartment is not specified, a ValueError is raised since the hole filling strategy depends on the compartment type.

    Returns
    -------
    np.ndarray
        3D instance segmented mask image with holes filled
    """
    if compartment is None:
        raise ValueError("Compartment must be specified for hole filling.")

    mask_ndim = mask.ndim

    mask_cp = cupy.asarray(mask)
    new_mask_cp = cupy.zeros_like(mask_cp)

    if compartment.lower() == "cell":
        for label in cupy.unique(mask_cp):
            label = int(label)
            if label == 0:
                continue
            tmp_mask = mask_cp == label
            tmp_mask = cupyx.scipy.ndimage.binary_fill_holes(
                tmp_mask,
            )
            if tmp_mask.ndim == 3:
                for z in range(tmp_mask.shape[0]):
                    tmp_mask[z] = cupyx.scipy.ndimage.binary_fill_holes(tmp_mask[z])
            elif tmp_mask.ndim == 2:
                tmp_mask = cupyx.scipy.ndimage.binary_fill_holes(tmp_mask)
            new_mask_cp[tmp_mask] = label
        mask = cupy.asnumpy(new_mask_cp).astype(mask.dtype)

    elif compartment.lower() == "organoid":
        new_mask_cp = cupyx.scipy.ndimage.binary_fill_holes(
            mask_cp,
        )
        if new_mask_cp.ndim == 3:
            for z in range(new_mask_cp.shape[0]):
                new_mask_cp[z] = cupyx.scipy.ndimage.binary_fill_holes(new_mask_cp[z])
        elif new_mask_cp.ndim == 2:
            new_mask_cp = cupyx.scipy.ndimage.binary_fill_holes(new_mask_cp)
        mask = cupy.asnumpy(new_mask_cp).astype(mask.dtype)
        mask = scipy.ndimage.label(mask)[0].astype(mask.dtype)

    return mask


def remove_small_objects_preserve_labels(
    segmentation_masks: np.ndarray,
    min_size: int = 250,
) -> np.ndarray:
    """
    Removes small objects given a minimum size while preserving the instance segmentation.

    Parameters
    ----------
    segmentation_masks : np.ndarray
        The instance segmented masks
    min_size : int, optional
        The minimum size of objects to keep, by default 250

    Returns
    -------
    np.ndarray
        The instance segmented masks with small objects removed
    """
    segmentation_masks = np.asarray(segmentation_masks)

    # Ensure integer labeled image for regionprops
    if not np.issubdtype(segmentation_masks.dtype, np.integer):
        segmentation_masks = skimage.measure.label(segmentation_masks > 0).astype(
            np.int32
        )

    props = skimage.measure.regionprops(segmentation_masks)

    for prop in props:
        if prop.area < min_size:
            segmentation_masks = np.where(
                segmentation_masks == prop.label, 0, segmentation_masks
            )

    return segmentation_masks
