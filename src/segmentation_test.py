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
from cellpose import models, plot, io as cellpose_io
import imageio
from segmentation import segment_nuclei, segment_cells


if './src' not in sys.path:
    sys.path.insert(0, './src')

warnings.filterwarnings('ignore')


def run_segmentation_test():
    DATA_DIR = 'data/'
    RESULTS_DIR = 'results/'
    os.makedirs(RESULTS_DIR, exist_ok=True)

    condition_dirs = sorted([d for d in glob.glob(os.path.join(DATA_DIR, '*')) if os.path.isdir(d)])


    #loop over each condition directory 
    for condition_dir in tqdm(condition_dirs, desc="Processing Conditions"):
        condition_name = os.path.basename(condition_dir)
        print(f"\\nProcessing 3 samples from condition: {condition_name}")
        
        condition_results_dir = os.path.join(RESULTS_DIR, condition_name)
        os.makedirs(condition_results_dir, exist_ok=True)
        
        nuc_dir = os.path.join(condition_dir, 'nuc', 'imgs')
        nuc_files = sorted(glob.glob(os.path.join(nuc_dir, '*.tif')))

        
        #process the first 3 images of the condition 
        for nuc_img_path in tqdm(nuc_files[:3], desc=f"Processing images in {condition_name}", leave=False):
            base_name = os.path.basename(nuc_img_path).replace('.tif', '')
            cyt_img_path = nuc_img_path.replace('_n.tif', '_c.tif').replace('/nuc/', '/cyt/')


            nuc_img = io.imread(nuc_img_path)
            cyt_img = io.imread(cyt_img_path)
            print(f"Analyzing image: {base_name}")
            nuc_masks = segment_nuclei(nuc_img, diameter=90)
            cell_masks = segment_cells(cyt_img, diameter=150)
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 15))
            fig.suptitle(f'Segmentation for {condition_name}\\n{base_name}', fontsize=16)
            
            nuc_overlay = plot.mask_overlay(nuc_img, nuc_masks)
            axes[0, 0].imshow(nuc_overlay)
            axes[0, 0].set_title('Nucleus Segmentation Overlay')
            axes[0, 0].axis('off')
            
            axes[0, 1].imshow(nuc_img)
            axes[0, 1].imshow(nuc_masks > 0, alpha=0.5)
            axes[0, 1].set_title('Nucleus Segmentation Details')
            
            cell_overlay = plot.mask_overlay(cyt_img, cell_masks)
            axes[1, 0].imshow(cell_overlay)
            axes[1, 0].set_title('Cell Segmentation Overlay')
            axes[1, 0].axis('off')
 
            axes[1, 1].imshow(cyt_img)
            axes[1, 1].imshow(cell_masks > 0, alpha=0.5)
            axes[1, 1].set_title('Cell Segmentation Details')
            axes[1, 1].axis('off')


            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            fig_path = os.path.join(condition_results_dir, f"{base_name}_segmentation_report.png")
            plt.savefig(fig_path)
            plt.close(fig)
            
            io.imsave(os.path.join(condition_results_dir, f"{base_name}_nuc_mask.tif"), nuc_masks.astype(np.uint16))
            io.imsave(os.path.join(condition_results_dir, f"{base_name}_cell_mask.tif"), cell_masks.astype(np.uint16))
            print(f"Saved masks and report for {base_name} to {condition_results_dir}")

if __name__ == '__main__':
    run_segmentation_test() 