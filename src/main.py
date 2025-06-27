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
from skimage.measure import regionprops_table
import trackpy as tp

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

    # --- Configuration ---
    DATA_DIR = 'data/'
    RESULTS_DIR = 'results/'
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Only needed when saving masks and visualizations
    #MASKS_DIR = os.path.join(RESULTS_DIR, 'masks')
    #os.makedirs(MASKS_DIR, exist_ok=True)
    #VISUALIZATION_DIR = os.path.join(RESULTS_DIR, 'visualizations')
    #os.makedirs(VISUALIZATION_DIR, exist_ok=True)

    all_results = []
    tracking_frames = []
    summary_list = []

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

            # Part 1 - Segmentation model

            nuc_mask = cpsam_segmentation(nuc_img, diameter=90)
            cell_mask = cpsam_segmentation(cyt_img, diameter=150)

            # removing cells touching the border to get a clean cell mask.
            cell_mask_cleared = remove_border_objects(cell_mask)

            # relabeling nuclei based on the cleared cell mask. This ensures that a nucleus with label "x" belongs to the cell with label "x".
            nuc_mask_relabeled = relabel_nuclei_by_cell_overlap(cell_mask_cleared, nuc_mask, overlap_threshold=0.5)

            # removing cells that do not have a corresponding nucleus assigned.
            final_cell_mask = filter_cells_without_nuclei(cell_mask_cleared, nuc_mask_relabeled)

            # extracts where each cell is at each timepoint
            props = regionprops_table(final_cell_mask, properties=['label', 'centroid'])
            df = pd.DataFrame(props)
            # Rename 'label' to 'particle' for TrackPy
            df.rename(columns={'label': 'particle'}, inplace=True)

            # Add time and condition info
            df['frame'] = time_point
            df['condition'] = condition_name

            tracking_frames.append(df)

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


    # Part 2 -  Tracking Cells
    tracking_df = pd.concat(tracking_frames, ignore_index=True)
    tracking_df.rename(columns={'centroid-0': 'y', 'centroid-1': 'x'}, inplace=True)

    if 'condition' not in tracking_df.columns:
        raise ValueError("Missing 'condition' column — make sure df['condition'] = condition_name is included")

    for condition in tracking_df['condition'].unique():
        condition_df = tracking_df[tracking_df['condition'] == condition].copy()

        # Run tracking
        linked_tracks = tp.link_df(condition_df, search_range=20, memory=2)

        # Save all tracks
        csv_all_path = os.path.join(RESULTS_DIR, f"tracked_cells_all_{condition}.csv")
        # linked_tracks.to_csv(csv_all_path, index=False)

        # fig_all, ax_all = plt.subplots(figsize=(6, 5))
        # tp.plot_traj(linked_tracks, ax=ax_all)
        # ax_all.set_title(f"All Cell Tracks – {condition}")
        # plot_all_path = os.path.join(RESULTS_DIR, f"cell_tracks_all_{condition}.png")
        # fig_all.savefig(plot_all_path, dpi=300, bbox_inches='tight')
        # plt.close(fig_all)

        # Filter short tracks
        filtered_tracks = linked_tracks.groupby('particle').filter(lambda x: len(x) > 10)

        # Save filtered tracks
        csv_filtered_path = os.path.join(RESULTS_DIR, f"tracked_cells_filtered_{condition}.csv")
        filtered_tracks.to_csv(csv_filtered_path, index=False)

        fig_filt, ax_filt = plt.subplots(figsize=(6, 5))
        tp.plot_traj(filtered_tracks, ax=ax_filt)
        ax_filt.set_title(f"Filtered Cell Tracks – {condition}")
        plot_filtered_path = os.path.join(RESULTS_DIR, f"cell_tracks_filtered_{condition}.png")
        fig_filt.savefig(plot_filtered_path, dpi=300, bbox_inches='tight')
        plt.close(fig_filt)

        # Tracking summary
        total_centroids = len(condition_df)
        used_centroids = len(filtered_tracks)
        dropped = total_centroids - used_centroids

        summary_list.append({
            'condition': condition,
            'total_centroids': total_centroids,
            'tracked_centroids': used_centroids,
            'dropped_centroids': dropped
        })

        print(f"[✔] {condition}: All = {total_centroids}, Tracked = {used_centroids}, Dropped = {dropped}")
        print(f"     ➤ Saved plots & CSVs to: {RESULTS_DIR}")

    # Save tracking summary
    summary_df = pd.DataFrame(summary_list)
    summary_df.to_csv(os.path.join(RESULTS_DIR, "tracking_summary.csv"), index=False)
    print(f"\n[✔] Tracking summary saved: {os.path.join(RESULTS_DIR, 'tracking_summary.csv')}")

    print("pipeline finished")

if __name__ == '__main__':
  main()