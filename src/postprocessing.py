import numpy as np
from skimage.morphology import erosion, disk
from skimage.measure import regionprops
import scipy.ndimage as ndi


def get_cytoplasm_mask(cell_mask, nuc_mask, shrink_pixels=5):
    """
    Defines the cytoplasm by first shrinking the cell mask (to exclude the membrane)
    and then subtracting the nucleus mask. 
    """

    selem = disk(shrink_pixels)

    # Eroding the cell mask to get the "inner cell"
    shrunken_cell_mask = np.zeros_like(cell_mask)
    for label in np.unique(cell_mask):
        if label == 0:
            continue
        cell_region = (cell_mask == label)
        eroded_region = erosion(cell_region, selem)
        shrunken_cell_mask[eroded_region] = label

    cytoplasm_mask = shrunken_cell_mask.copy()
    cytoplasm_mask[nuc_mask > 0] = 0

    return cytoplasm_mask


def get_membrane_mask_and_shrunken_cells(cell_mask, shrink_pixels=5):
    """
    Membrane is defined by shrinking each cell mask and subtracting the shrunken version.
    """
    shrunken_cells = np.zeros_like(cell_mask)
    selem = disk(shrink_pixels)
    
    cell_labels = np.unique(cell_mask)
    cell_labels = cell_labels[cell_labels != 0]

    for label in cell_labels:
        single_cell_mask = (cell_mask == label)
        eroded_cell = erosion(single_cell_mask, selem)
        
        shrunken_cells[eroded_cell] = label
            

    membrane_mask = cell_mask - shrunken_cells
    
    return membrane_mask, shrunken_cells


def remove_border_objects(mask_image):
    """
    Removes objects from a labeled mask that are touching the border of the image.

    """
    
    cleared_mask = np.copy(mask_image)
    
    # getting the labels of objects touching the border
    border_mask = np.zeros_like(mask_image, dtype=bool)
    border_mask[0, :] = True
    border_mask[-1, :] = True
    border_mask[:, 0] = True
    border_mask[:, -1] = True
    
    border_labels = np.unique(mask_image[border_mask])
    
    for label in border_labels:
        if label == 0:  # to not remove the background
            continue
        cleared_mask[cleared_mask == label] = 0
        
    return cleared_mask 