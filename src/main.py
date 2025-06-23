import os
import sys
import glob
import re
import numpy as np
import pandas as pd
from skimage import io
from tqdm import tqdm
import warnings
import matplotlib.pyplot as plt
from cellpose import models, plot, core, io as cellpose_io

# adding src to the path to import custom modules
if './src' not in sys.path:
    sys.path.insert(0, './src')

from segmentation import segment_nuclei, segment_cells, cpsam_segmentation
from postprocessing import get_cytoplasm_mask,get_membrane_mask_and_shrunken_cells, remove_border_objects, relabel_nuclei_by_cell_overlap, filter_cells_without_nuclei
from measurement import measure_intensities
from plotting import plot_nc_ratio, plot_membrane_signal

warnings.filterwarnings('ignore')

def main():
    """
    main function to run the image analysis pipeline.
    """
    print ("analysis pipeline")
    
    # configuration
    DATA_DIR = 'data.nosync/'
    RESULTS_DIR = 'results/'
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # only needed when saving masks and visualizations
    #MASKS_DIR = os.path.join(RESULTS_DIR, 'masks')
    #os.makedirs(MASKS_DIR, exist_ok=True)
    #VISUALIZATION_DIR = os.path.join(RESULTS_DIR, 'visualizations')
    #os.makedirs(VISUALIZATION_DIR, exist_ok=True)
    
    all_results = []

    
    condition_dirs = sorted([d for d in glob.glob(os.path.join(DATA_DIR, '*')) if os.path.isdir(d)])
    if not condition_dirs:
        print("No condition directories found in the 'data' folder.")
        return

    for condition_dir in tqdm(condition_dirs, desc="Processing Conditions"):
        condition_name = os.path.basename(condition_dir)
        nuc_dir = os.path.join(condition_dir, 'nuc', 'imgs')
        nuc_files = sorted(glob.glob(os.path.join(nuc_dir, '*.tif')))


        for nuc_img_path in tqdm(nuc_files, desc=f"Analyzing {condition_name}", leave=False):
            # loading images
            base_name = os.path.basename(nuc_img_path)
            time_point_match = re.search(r'_t(\d+)_', base_name)
            if not time_point_match:
                continue
            time_point = int(time_point_match.group(1))
            
            cyt_img_path = nuc_img_path.replace('_n.tif', '_c.tif').replace('/nuc/', '/cyt/')
            if not os.path.exists(cyt_img_path):
                continue
            
            nuc_img = io.imread(nuc_img_path)
            cyt_img = io.imread(cyt_img_path)

            # segmentation model

            nuc_mask = cpsam_segmentation(nuc_img, diameter=90)
            cell_mask = cpsam_segmentation(cyt_img, diameter=150)

            # removing cells touching the border to get a clean cell mask.
            cell_mask_cleared = remove_border_objects(cell_mask)

            # relabeling nuclei based on the cleared cell mask. This ensures that a nucleus with label "x" belongs to the cell with label "x". 
            nuc_mask_relabeled = relabel_nuclei_by_cell_overlap(cell_mask_cleared, nuc_mask, overlap_threshold=0.5)

            # removing cells that do not have a corresponding nucleus assigned.
            final_cell_mask = filter_cells_without_nuclei(cell_mask_cleared, nuc_mask_relabeled)
            
            # generating masks
            membrane_mask, shrunken_cells = get_membrane_mask_and_shrunken_cells(final_cell_mask, shrink_pixels=5)
            cytoplasm_mask = get_cytoplasm_mask(final_cell_mask, nuc_mask_relabeled, shrink_pixels=5)

            # saving masks for visualization 
            #base_savename = os.path.basename(nuc_img_path).replace('_n.tif', '')
            #mask_path = os.path.join(MASKS_DIR, f"{base_savename}_cell_mask.tif")
            #io.imsave(mask_path, final_cell_mask.astype(np.uint16), check_contrast=False)
            #io.imsave(os.path.join(MASKS_DIR, f"{base_savename}_nuc_mask.tif"), nuc_mask_relabeled.astype(np.uint16))
            #io.imsave(os.path.join(MASKS_DIR, f"{base_savename}_cell_mask_cleared.tif"), final_cell_mask.astype(np.uint16))
            #io.imsave(os.path.join(MASKS_DIR, f"{base_savename}_cyto_mask.tif"), cytoplasm_mask.astype(np.uint16))
            #io.imsave(os.path.join(MASKS_DIR, f"{base_savename}_membrane_mask.tif"), membrane_mask.astype(np.uint16))


            #fig, axes = plt.subplots(2, 2, figsize=(15, 15))
            #fig.suptitle(f'Segmentation for {condition_name}\\n{base_savename}', fontsize=16)

            #axes[0, 0].imshow(plot.mask_overlay(nuc_img, nuc_mask_relabeled))
            #axes[0, 0].set_title('Cleaned & Relabeled Nucleus Mask')
            #axes[0, 0].axis('off')
            
            #axes[0, 1].imshow(plot.mask_overlay(cyt_img, final_cell_mask))
            #axes[0, 1].set_title('Final Cleaned Cell Mask')
            #axes[0, 1].axis('off')

            #axes[1, 0].imshow(plot.mask_overlay(cyt_img, cytoplasm_mask))
            #axes[1, 0].set_title('Cytoplasm Mask')
            #axes[1, 0].axis('off')

            #axes[1, 1].imshow(plot.mask_overlay(cyt_img, membrane_mask))
            #axes[1, 1].set_title('Membrane Mask')
            #axes[1, 1].axis('off')
            
            #plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            #fig_path = os.path.join(VISUALIZATION_DIR, f"{base_savename}_segmentation_report.png")
            #plt.savefig(fig_path, dpi=300)
            #plt.close(fig)

            # measurement 
            results_df = measure_intensities(
                nuc_mask=nuc_mask_relabeled,
                cyto_mask=cytoplasm_mask,
                mem_mask=membrane_mask,
                nuc_signal=cyt_img,  
                cell_signal=cyt_img
            )
            
            results_df['condition'] = condition_name
            results_df['time_point'] = time_point
            all_results.append(results_df)


        
    master_df = pd.concat(all_results, ignore_index=True)
    
    # saving master results table
    output_csv_path = os.path.join(RESULTS_DIR, 'master_results.csv')
    master_df.to_csv(output_csv_path, index=False)
    print(f"\nmaster results table saved to: {output_csv_path}")
    
    # generating and saving plots
    plot_nc_ratio(master_df, RESULTS_DIR)
    plot_membrane_signal(master_df, RESULTS_DIR)
    
    print("pipeline finished")

if __name__ == '__main__':
    main() 