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


def relabel_nuclei_by_cell_overlap(cell_mask, nuc_mask, overlap_threshold=0.5):
    """
    Relabels nuclei based on the label of the cell they are inside.

    A nucleus is assigned the label of a cell if the nucleus area overlaps
    with the cell area by at least the specified threshold. This ensures that a 
    nucleus label in the output mask corresponds to the same cell label in the cell mask.


    """
    new_nuc_mask = np.zeros_like(nuc_mask)
    nuc_labels = np.unique(nuc_mask)
    nuc_labels = nuc_labels[nuc_labels != 0]

    for nuc_label in nuc_labels:
        nuc_region_mask = (nuc_mask == nuc_label)
        
        # Find all cell labels that overlap with this nucleus and ignore background pixels (label 0)
        overlapping_cell_labels = cell_mask[nuc_region_mask]
        overlapping_cell_labels = overlapping_cell_labels[overlapping_cell_labels != 0]

        if overlapping_cell_labels.size == 0:
            continue

        # find the most common cell label this nucleus overlaps with

        unique_labels, counts = np.unique(overlapping_cell_labels, return_counts=True)
        parent_cell_label = unique_labels[np.argmax(counts)]

        # apply the soft threshold 
        nuc_area = np.sum(nuc_region_mask)
        overlap_area = np.max(counts)
        
        if (overlap_area / nuc_area) > overlap_threshold:
            new_nuc_mask[nuc_region_mask] = parent_cell_label

    return new_nuc_mask


def filter_cells_without_nuclei(cell_mask, nuc_mask):
    """
    Filters out cells from a cell mask that do not have a corresponding nucleus. 
    This function assumes that the nucleus mask has already been relabeled so that nucleus labels correspond to their parent cell labels. 
    It removes any cell from the cell_mask that does not have a corresponding nucleus in the nuc_mask.
    """
    # get the unique labels of cells that actually have a nucleus.
    labels_with_nuclei = np.unique(nuc_mask)
    
    # new mask that only keeps cells whose labels are in labels_with_nuclei.

    filtered_cell_mask = np.copy(cell_mask)
    pixels_to_keep = np.isin(filtered_cell_mask, labels_with_nuclei)
    
    # setting all pixels belonging to cells without a nucleus to 0.
    filtered_cell_mask[~pixels_to_keep] = 0
    
    return filtered_cell_mask 