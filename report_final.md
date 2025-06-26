



























Quantifying Subcellular Dynamics of β-Catenin in HAP1 Cells







Group 9 - Image Processing






\newpage


1. Introduction


In this project, we investigate the subcellular localization dynamics of β-catenin (CTNNB1), a multifunctional protein involved in both cell adhesion and Wnt signaling pathway, as depicted in Figure 1. Upon Wnt signaling activation, CTNNB1 accumulates in the nucleus where it alters gene expression patterns. As the Wnt signal terminates, the protein is degraded in the cytoplasm via the proteasomeal mechanism, aided by effector proteins, such as GSK3β, which flag CTNNB1 for downstream degradation. [1]



![](media/figure_10.png)
Figure 1: Mechanism of action of Wnt signal activation (left) and mechanism of  β-catenin (CTNNB1) degradation in Wnt signal deactivation (right). [1]

Our goal is to quantify changes in β-catenin localization by measuring the membrane signal and nuclear-to-cytoplasmic signal ratio across three different experimental conditions in HAP1 cells. The conditions include untreated control, treatment with Wnt3a and  CHIR-99021. Wnt3a is a ligand that stimulates the Wnt signalling pathway (Figure 1, left) and CHIR-99021 is a GSK3β inhibitor, which blocks proteasomal degradation of CTNNB1 in the cytoplasm (Figure 1, right).


All in all our research question is, whether localization of CTNNB1 in the cell changes significantly across the observed control and treatment conditions. For this purpose quantitative data analysis was performed on the data set images using Python, Cellpose and ImageJ (FIJI).



2. Experimental dataset



The dataset we are working with consists of fluorescence microscopy .tif images of HAP1 cells captured under three conditions: untreated control, stimulation with Wnt3a (100 ng/mL), and treatment with CHIR-99021 (4 μM).


The images were organized into three subfolders, one for control and two for case experiments. Within each condition folder, two subfolders are present, namely cyt/ for the CTNNB1 cytoplasmic signal and nuc/ for the nuclear marker, representing two separate imaging channels captured per time point. Each subfolder contains time-lapse image sequences with 96 frames, stored under informative labels containing experimental condition, imaging position, and time frame tags. For each timepoint, paired grayscale images are available: one capturing nuclear signal (nuc/) and the other cell-wide CTNNB1 signal (cyt/).


As mentioned, each image file is named using a standardized convention that embeds important metadata. For example, the filename 220216 FW006B3 HAP1_Position002_Control_t000_c.tif can be interpreted as follows; 220216 represents the acquisition date (February 16, 2022), FW006B3 HAP1_Position002_Control identifies the sample, imaging position and experimental condition, t000 is the time point index and c or n tags the imaging channel, representing cytoplasm or nucleus respectively. This naming scheme ensures that cytoplasmic and nuclear images for each timepoint can be reliably matched for downstream analysis.


Folder organization hierarchy is visualised in Figure 2 below.


![](media/figure_3.png)
Figure 2: Visualization of folder hierarchy in the data set. 




3. Image Processing Quantitative Data Analysis Pipeline

3.1 Workflow 


The overall workflow of our Image Processing Quantitative Data Analysis pipeline is presented in Figure 3 below.

![](media/Screenshot%202025-06-26%20at%2022.34.09.png)
Figure 3: Image Processing Quantitaive Data Analysis workflow.


3.2 Image Segmentation Pipeline


3.2.1 Cellpose (Pre-trained models)

Firstly, the cells and nuclei were segmented from the images using a pre-trained Deep Learning Cellpose model. For segmenting nuclei we used model type nuclei and for cells cyto2. 

The only hyperparameters used were nuclear and cytoplasmic diameter, for which we tried various values. We started with a nuclear diameter of 40 and cell diameter of 90. The results showed a promising segmentation performance at a cellular level, however, the segmentation was much worse for nuclei (Figure 4, A). To improve the model setup we used FIJI to estimate the average diameters of nuclei and cells from the images, using ROI measurement tools. Based on observations we set nuclear diameter to 90 and cytoplasmic diameter to 150. This significantly improved nuclear segmentation, as the model was now able to detect larger nuclei areas. Cellular segmentation performance also improved slightly (Figure 4, B). An additional experiment was performed with even larger nucleus and cellular diameters (120, 200 respectively), however, the segmentation performances worsened. We observed smaller nuclei were missed and some detected nuclei were merged together. The latter was also observed at a cellular level (Figure 4, C).


![](media/figure_8.png)
Figure 4: Segmentation of nuclei and cells using nuclei and cyto2 pre-trained models from Cellpose using variable hyperparameters. A - Nuclear diameter was set to 40 and cell diameter to 94. B - Nuclear diameter was set to 90 and cell diameter to 150. C - Nuclear diameter was set to 120 and cell diameter to 200. All examples are shown on images at time frame 0 for the control experiment (220216 FW006B3 HAP1_Position002_Control_t000_n (top) and 220216 FW006B3 HAP1_Position002_Control_t000_c (bottom)).


All in all, we concluded the hyperparameter diameters of 90 and 150 (Figure 4, B) provide the best segmentation results. However, as especially for nuclei the model still underperformed, we opted for a better image segmentation approach.


3.2.2 SAM-Cellpose



To improve our segmentation results, we employed the Segment Anything Model (SAM) from Cellpose, an enhanced deep-learning architecture built upon the original framework. SAM-Cellpose incorporates improvements that significantly boost performance across diverse cell types and imaging conditions. Unlike nuclei and cyto2 models, it is trained on a larger and more varied dataset, and demonstrates superior generalization without the need for manual annotation or fine-tuning. Benchmarking studies show that SAM often achieves higher accuracy and cleaner boundary segmentation, compared to human-annotated masks. Given its robustness and state-of-the-art performance, this was the default model we used for both nucleus and cytoplasm segmentation in our pipeline. [2]


In accordance with our findings with the basic Cellpose algorithm, nuclear and cytoplasmic diameter hyperparameters for SAM were defined as 90 and 150, respectively. The segmentation performance significantly improved, and can be viewed in Figure 5 below.

![](media/Screenshot%202025-06-26%20at%2022.40.17.png)
Figure 5: Segmentation of nuclei and cells using SEM Cellpose model, using hyperparameters 90 and 150 for nuclear and cell diameter respectively. This example is shown on images at time frame 0 for the control experiment (220216 FW006B3 HAP1_Position002_Control_t000_n (left) and 220216 FW006B3 HAP1_Position002_Control_t000_c (right)).



3.3 Mask Extraction and Processing



At this point in our analysis pipeline, we have already obtained the raw nuclear and cell masks for each image. These were then post-processed and informative masks for the three cellular regions of interest were extracted, namely nucleus, cytoplasm and cell membrane.



Post-processing started with removing edge case cells from cell masks. After that each nucleus was assigned by spatial overlap to a cell using a soft threshold condition after one-to-one matching failed to provide good results. As visualised in Figure 6, only a few nuclei were matched to cells, as being fully in the cells, using a basic one-to-one matching approach. We assume this is due to the large nuclear size and consequent overlap of nuclear with cellular borders.

![](media/Screenshot%202025-06-26%20at%2022.52.20.png)
Figure 6: Visualization of one-to-one nucleus to cell matching and edge-case cell removal. On the left image we see that only a few nuclei were matched to the cells (coloured). On the right side we see all remaining cells, after the edge cases were removed (coloured). This example is shown on images at time frame 0 for the control experiment (220216 FW006B3 HAP1_Position002_Control_t000_n (left) and 220216 FW006B3 HAP1_Position002_Control_t000_c (right)).





Our soft thresholding approach thus employed code that iterated through each nucleus in the nuclear mask. By spatially matching nucleus pixels with the cell mask, it identified the label of the most likely parent cell for each nucleus. If 50% or more of the nucleus pixels overlapped with the cell area, we assigned that nucleus to the cell by label matching. With this threshold, we ensured that the matching was significant. As a result, a new corrected nucleus mask was created in which the label of each nucleus matched the label of its parent cell in the paired image cell mask. Nuclei that were not assigned to any single cell were considered artefacts and discarded, meaning interpreted as background in the corrected nuclear mask. Additionally, cells in which no nucleus was found were discarded as well. The latter helped us recognise and remove false positives in cell segmentation, namely background regions or gaps that might have been mistaken for cells. The results of soft threshold matching and the post-processing steps are presented in Figure 7.

![](media/Screenshot%202025-06-26%20at%2022.53.31.png)
Figure 7: Visualization of results of nucleus to cell matching using a soft threshold (0.5) and post-processing steps. On the left side, colours indicate nuclei that were matched successfully. On the right side the colours  indicate all remaining cells, after removal of edge cases and cells without a nucleus. This example is shown on images at time frame 0 for the control experiment (220216 FW006B3 HAP1_Position002_Control_t000_n (left) and 220216 FW006B3 HAP1_Position002_Control_t000_c (right)).




To obtain the cytoplasmic mask, the membrane regions were excluded by eroding 5 pixels from the edge of each cell in the cell mask (Figure 8, A). From this shrunken cell mask, the corresponding nucleus from the nuclear mask was subtracted (Figure 8, B).



The membrane mask was obtained by subtracting the shrunken cell mask, created as previously described, from the original cell mask, effectively retaining only 5 pixel borders of cells (Figure 8, C).

![](media/figure_7.png)
Figure 8: Visualization of the process of creation of cytoplasm and membrane masks. A - Five pixel erosion in the cell mask to obtain the shrunken cell mask. B - Subtraction of nuclei from the shrunken cell mask to obtain the final cytoplasm mask. C - Subtraction of shrunken cell mask from the original cell mask to obtain the final membrane mask. This example is shown on cell image at time frame 0 for the control experiment (220216 FW006B3 HAP1_Position002_Control_t000_c).





An example of the final binary nucleus, cytoplasm and cell membrane masks extracted from the same image is presented in Figure 9 below.

![](media/figure_12.png)
Figure 9: Final binary compartment masks extracted from images at time frame 0 for the control experiment (220216 FW006B3 HAP1_Position002_Control_t000_n, 220216 FW006B3 HAP1_Position002_Control_t000_c). A - Final nucleus mask. B - Final cytoplasm mask. C - Final cell membrane mask. 



3.4. Signal Quantification and Output



3.4.1 Intensity Measurements



To quantify the distribution of CTNNB1 within individual cells, we measured signal intensities in three distinct subcellular compartments, the nucleus, cytoplasm and membrane.



For each compartment in each image, we overlaid the corresponding mask on the cytoplasmic fluorescence channel. We then applied the regionprops function from the skimage.measure module, which computes region-based statistics, to measure the mean signal intensity within each labeled mask. By doing this for each compartment, we extracted its per-cell intensity profile across time and conditions. The resulting measurements were stored in a structured data frame and exported as a .csv file (master_results.csv) for further statistical analysis. The first five rows of the results data frame are presented in Table 1 below.

Table 1: A five-row section of the master_results.csv data frame containing per-cell measurement results. The first column label contains numeric labels of cells in an image. Column nuc_mean_intensity contains the mean intensities of pixels in the nuclei. Likewise, cyto_mean_intensity and mem_mean_intesity hold mean pixel intensities of cytoplasms and membranes. Condition and time point of the image are noted in condition and time_point.
![](media/figure_13.png)



3.4.2 Plots


To interpret how CTNNB1 localization changes over time and under different experimental conditions, we generated two types of summary plots. The first plot displays the nuclear-to-cytoplasmic (N/C) signal ratio of CTNNB1 across timepoints (Figure 10). For each condition, individual cell measurements were used to compute the mean N/C ratio at each timepoint. The second plot shows the normalized membrane intensity, calculated per cell by dividing each timepoint’s membrane signal by its own initial value at frame zero (Figure 11). This normalization allows for tracking relative changes over time regardless of baseline differences across conditions.



Both plots were generated using the seaborn library with line plots representing the mean values and shaded regions indicating the 95% confidence intervals. These shaded areas visually reflect the variability and reliability of the measurements, where narrower bands suggest consistent behavior across cells and wider bands indicate more heterogeneous responses. All plots were saved as high-resolution .png files.


![](media/figure_11.png)
Figure 10: Mean nuclear-to-cytoplasmic (N/C) signal ratio of CTNNB1 over time for each experimental condition. Each point represents the average N/C ratio computed across individual cells at a given time point. Shaded regions visualize the 95% confidence interval. 


![](media/figure_16.png)
Figure 11: Normalized membrane intensity of CTNNB1 over time. Membrane signal values were normalized to their initial intensity at frame zero. The mean trajectory per condition is shown with a shaded 95% confidence interval.



In Figure 10 we see a stronger increase in nuclear to cytoplasmic CTNNB1 ratio over time in both Wnt3a and CHIR conditions compared to control. In both treatments the N/C ratio reaches its maximum around time frame 50. For Wnt3a it plateaus after that and for CHIR it starts to decrease. Overall the responses to both conditions seem very similar with high overlap in the noisy 95% confidence intervals. Even in the control experiment we see a slight time-dependent increase in N/C ratio.



In Figure 11 we see similar trends in membrane CTNNB1 signals over time. In both conditions the signal shows a stronger increase with time compared to the control, however, with a slight delay of 20 time frames after time 0. The signal also reaches its maximum around time frame 60 and decreases after that in both treatment conditions. In contrast with the N/C ratio, a slight time-dependent decrease in membrane signal is observed in the control experiment. The 95% confidence intervals, however, still show high variability of data relative to mean values.



3.5 Statistical Analysis


To assess whether the subcellular measurements differed significantly over time and between conditions, we fitted simple ordinary least squares (OLS) linear models separately for two response variables, namely the nuclear-to-cytoplasmic signal ratio and normalized membrane intensity. The models took control as the baseline condition, to which Wnt3 and CHIR conditions were compared. The effects of condition and time point were evaluated, as well as their interaction, allowing us to test whether temporal trends in signal behavior differed across treatment groups.



Each row in the analyzed master_results.csv dataset corresponded to a single measurement, and due to the lack of consistent cell tracking via labels across time points, no repeated-measures structure was modeled. The results of the model fit for the nuclear to cytoplasmic signal ratio are presented in Table 2 and for the normalized membrane signal intensity in Table 3.

Table 2: Ordinary least squares (OLS) model results for the nuclear-to-cytoplasmic (N/C) signal ratio of CTNNB1. The table shows coefficient values, their associated t-statistics and p-values. Significant p-values (below 0.05) are highlighted in bold. 
![](media/figure_5.png)

Table 3: Ordinary least squares (OLS) model results for the normalized membrane signal intensity of CTNNB1. The table shows coefficient values, their associated t-statistics and p-values. Significant p-values (below 0.05) are highlighted in bold. 
![](media/figure_4.png)




We found that both CHIR and Wnt3a treatments significantly increased the baseline nuclear-to-cytoplasmic (N/C) CTNNB1 ratio relative to control. Statistically insignificant, slightly negative interaction term for CHIR and time suggests that the rate of increase in nuclear accumulation over time was not significantly different from the control group.  On the other hand, Wnt3 condition showed a positive time-dependent increase in N/C ratio, therefore only Wnt3a seems to induce a statistically significant change in the time trajectory compared to control. Independent of treatment, time shows a strong positive effect on N/C ratio in the control condition, suggesting that CTNNB1 accumulates in the nucleus over time even without stimulation.



In the membrane compartment, both CHIR and Wnt3a treatments significantly increased baseline CTNNB1 intensity compared to the control condition. While membrane intensity showed a slight decrease over time in the control group, this trend was significantly reversed in the treatment groups. Both CHIR and Wnt3a significantly altered the trajectory of membrane signal over time, with Wnt3a exhibiting a stronger temporal increase.




1. Cell tracking



The objective of the tracking step was to monitor individual cells over time across microscopy frames in order to quantify their movement under different experimental conditions. This analysis aimed to understand cellular dynamics and potentially identify differences in movement dynamics between the control and treatment groups.



4.1 ImageJ


We initially attempted to perform cell tracking using ImageJ with the TrackMate plugin. In the image metadata, the T dimension was set from 0 to 0, indicating that the data consisted of a single 2D slice, while the Z dimension ranged from 0 to 95, representing 96 time frames of that 2D slice. During setup, we selected the LoG (Laplacian of Gaussian) detector for spot detection. 

However, the results were suboptimal (see figure 12); even after adjusting thresholding parameters, the plugin failed to produce reliable or accurate tracking. The LoG detector identified spots within cells, but performance was inconsistent: multiple centroids were placed within single cells, and boundary detection was poor. Due to these limitations, we decided to switch to TrackPy, which offered more consistent and customizable tracking capabilities within our Python-based pipeline.

![](media/figure_6.png)
Figure 12: Preview of TrackMate detection on the control condition using ImageJ.



4.2 TrackPy

TrackPy is a package used for tracking blob-like features over time and recording their trajectories based on the Crocker-Grier algorithm [3]. The algorithm selects frame-to-frame linking that globally minimizes the sum of the squared displacements. 

After segmentation, each cell in a given frame was assigned a unique label. Using the regionprops_table() function from the skimage library, we extracted the centroid coordinates (x, y) for each labeled region along with the corresponding frame number and condition name. These centroids were compiled into a single tracking data frame that served as input for the tracking algorithm.

We used the trackpy library to track cells across 96 time frames in our microscopy dataset. The search_range parameter was set to 20 pixels, which corresponds to approximately 13% of the average cell diameter (~150 pixels). This value reflects the expected physical displacement of a cell between consecutive frames and helps ensure that only biologically plausible movements are linked. The memory parameter was set to 2, allowing cells to temporarily disappear for up to two frames, for example, due to segmentation errors or transient signal loss, and still be reconnected as a single continuous trajectory. After tracking, we applied a filtering step to retain only those trajectories that spanned more than 10 frames, thereby removing short-lived or noisy tracks and focusing the analysis on sustained, biologically meaningful movements. This combination of parameters provided a good balance between sensitivity and specificity in cell tracking. For each condition, we saved the filtered trajectories as .csv files and generated static trajectory plots as .png images (Figure 13,14 and 15). Additionally, a final summary .csv file was created to log the number of total detections, the number of successfully tracked cells, and the number of detections that were dropped or discarded due to insufficient tracking length.

Table 4: Summary Table of tracked trajectories.
![](media/Screenshot%202025-06-26%20at%2023.27.32.png)


It’s possible that in the CHIR and Wnt3a conditions, the translocation of CTNNB1 to the nucleus alters nuclear morphology or contrast, which may impact segmentation quality. Since tracking relies on identifying and linking centroids across frames, any change in how consistently nuclei or cells are detected can reduce the number of trajectories that meet the filtering criteria. In contrast, the control condition, where CTNNB1 remains largely at the membrane and cytoplasm, might preserve clearer nuclear and cell boundaries, resulting in more stable centroid detection and longer trajectories.

Another challenge in the current tracking pipeline arises from the fact that segmentation is performed independently on each frame. While TrackPy does not require consistent labeling of cells across time, it relies on accurately detecting centroids and maintaining spatial continuity to reconstruct trajectories. When segmentation varies between frames—for instance, if a cell is missed, split, or slightly shifted—TrackPy may fail to associate centroids correctly, leading to fragmented or short-lived tracks. This can inflate the apparent number of cells and result in discontinuous trajectories. Additionally, with the memory parameter set to 2, TrackPy allows cells to temporarily disappear and reappear, which may cause "teleporting" tracks that skip over intermediate positions. These limitations are often difficult to detect in static trajectory plots and can be exacerbated by overlapping cells or poor signal-to-noise ratios.
An area for improvement in our pipeline would be to quantify the duration of each trajectory by tracking how many frames each one persisted. This would provide deeper insight into the quality and stability of the trajectories and help distinguish between consistently tracked cells and those with fragmented or short-lived paths. Additionally, generating time-lapse videos of tracked cells would allow for more intuitive visualization of trajectory dynamics and potential biological behaviors. Beyond TrackPy’s displacement-minimization approach, more advanced tracking algorithms—such as those based on Kalman filters—could be explored. These methods are generally more robust to noise and are capable of predicting future positions based on prior motion, potentially leading to more accurate and continuous tracking in noisy or complex datasets.

![](media/Screenshot%202025-06-26%20at%2023.43.06.png)
Figure 13: Filtered cell trajectories for the control condition (220216 FW006B3 HAP1_Position002_Control) showing only those cells that were successfully tracked across more than 10 frames. Each colored path represents the movement of a single cell over time, demonstrating relatively stable and continuous tracking performance under control conditions.


![](media/Screenshot%202025-06-26%20at%2023.46.23.png)
Figure 14: Filtered cell trajectories for the control condition (220216 FW006B3 HAP1_Position008_Wnt3a) showing only those cells that were successfully tracked across more than 10 frames. Each colored path represents the movement of a single cell over time, demonstrating relatively stable and continuous tracking performance under control conditions. 

![](media/Screenshot%202025-06-26%20at%2023.49.12.png)
Figure 15: Filtered cell trajectories for the control condition (220216 FW006B3 HAP1_Position005_CHIR 4muM) showing only those cells that were successfully tracked across more than 10 frames. Each colored path represents the movement of a single cell over time, demonstrating relatively stable and continuous tracking performance under control conditions. 





5. Instrumentation and Performance

This section contains instructions on how to run the code. 

Prerequisites
To run this project, you need to have Conda installed.

Environment Setup
1.) Create the Conda environment from the provided environment.yml file. This will install all the necessary libraries.
   conda env create -f environment.yml

2.) Activate the created environment.
   conda activate IQDPA

Running the Analysis Pipeline
The main part of the project is the image analysis pipeline that processes raw images to produce quantitative data and relevant plots.

Usage
You can run the pipeline using either a Python script or a Jupyter Notebook. Jupyter Notebook version also executes Cell Tracking pipeline

- For local execution with a GPU:
  python src/main.py

- For environments like Google Colab:
  Run the src/main.ipynb notebook.

Pipeline Output
The main pipeline generates the following files in the results/ directory:
- master_results.csv: A table that contains intensity measurements for each segmented cell.
- membrane_signal.png: A plot visualizing the normalized membrane signal across different conditions over time.
- nuclear_cytoplasmic_ratio.png: A plot visualizing the nuclear-to-cytoplasmic intensity ratio across conditions over time.
- cell_tracks_filtered_…_.png: Plot visualizing the filtered trajectories per conditions. 
- tracked_cells_filtered_…_.csv: A table visualizing the coordinates of each particle/cell per frame per condition.
- tracking_summary.csv: The summary table reports, for each condition, the total number of detected centroids across all frames, how many formed valid trajectories spanning more than 10 frames, and how many were dropped due to insufficient tracking length or fragmentation.

Running the Statistical Analysis
After running the main pipeline, you can run the statistical analysis script to produce statistics.

Usage
  python src/statistical_analysis.py

Statistical Output
This script uses the master_results.csv file as input and produces two new files in the results/ directory:
- membrane_stats_model_results.csv: Results of the statistical model for membrane intensity.
- nuc_cyto_ratio_stats_model_results.csv: Results of the statistical model for the nuclear-to-cytoplasmic ratio.


Helper Scripts
- measurement.py: Measure mean intensities of nucleus, cytoplasm and membrane masks for each cell.
- plotting.py: Contains helper functions for plotting Nuclear/Cytoplasmic ratio signal and membrane signal over time.
- postprocessing.py: Contains functions for finding cytoplasm and membrane masks,  removing border objects, and assigning cell label to nuclei.
- segmentation.py: Pretrained cell segmentation models. 


Performance
The processing time for the pipeline is dependent on the available GPU. We ran the main pipeline for three experimental conditions on Google Colab with an NVIDIA A100 GPU, which took approximately 1.5 hours (around 30 minutes per condition).
The tqdm library is used to provide real-time progress bars during execution. 



6. Summary of Results and Conclusions



In summary, our research highlighted efficient and inefficient image processing techniques, as well as gave insight into CTNNB1 localization dynamics across three different experimental conditions (control, Wnt3a and CHIR treatment) in HAP1 cells.


From a technical perspective, we found that SAM-Cellpose is a highly efficient approach for cell segmentation of both the nuclei and cells. The optimal hyperparameters for segmentation of HAP1 cells in our dataset were 90 and 150 for nucleus and cytoplasm diameters, respectively. In matching nuclei to cells, a soft thresholding approach, with a threshold of 0.5, worked much better than one-to-one matching. Furthermore, discarding cells with no matched nuclei allowed us to filter out false positives in cell segmentation, which served as an additional quality control measure.

A comment is also needed on our approach to statistical analysis. Although ordinary least squares (OLS) regression assumes linearity, we selected this approach to provide a straightforward statistical comparison of trends across treatment conditions and over time, compared to control. The goal was to test for general directional effects of treatments and assess their statistical significance rather than precisely model the complex dynamics of CTNNB1 localization. We acknowledge that the observed trends are non-linear, and that this approach is suboptimal.  However, because individual cells were not tracked consistently across time points, we could not account for within-cell variability or repeated measures. In future studies, consistent manual or automated cell tracking could enable the use of linear mixed-effects models, which would better account for subject-level variation and improve the robustness of temporal inferences.



In cell tracking experiments we found _______________. Insert Recap/description of the best approach here :)











From a biological point of view, our research question was whether localization of CTNNB1 in HAP1 cells changes significantly across the observed control and treatment conditions. The resulting plots and statistical analysis suggest both treatment conditions (Wnt3a and CHIR) significantly alter spatial distribution of CTNNB1, in terms of nuclear-to-cytoplasmic signal ratio and membrane signal, compared to the control, over time.



As Wnt3a initiates the Wnt signalling pathway and CHIR blocks CTNNB1 degradation, it was expected that in both treatments the nuclear-to-cytoplasmic signal ratio would be higher than in control. Our findings confirm these expected trends. They show relocation of CTNNB1 from the cytoplasm to the nucleus at first and then stabilisation of the nuclear-to-cytoplasmic ratio in Wnt3a treatment and a slight decrease with CHIR. The latter may reflect differences in regulatory feedback and signal duration. Wnt3a activates the full Wnt signaling cascade, which also includes transcriptional feedback mechanisms that may modulate CTNNB1 levels over time. In contrast, CHIR specifically inhibits GSK3β and prevents degradation, but without upstream ligand binding and receptor activation, it might lead to non-physiological accumulation and eventual adaptation or downregulation through alternative pathways. Additionally, the decrease in CHIR could reflect cytoplasmic retention, enhanced nuclear export, or transcriptional silencing of CTNNB1 targets as a feedback mechanism. Even in the control experiment a small significant time-dependent increase in the ratio was observed, suggesting an underlying natural flow of CTNNB1 from the cytoplasm to the nucleus.



In the membrane CTNNB1 signal, similar trends were observed. Both Wnt3a and CHIR significantly increased the levels of CTNNB1 located in and near the membrane compared to the control. Over time, membrane intensity in the control group slightly declined, suggesting normal redistribution of the protein away from the membrane. In contrast, both treatments significantly altered this trajectory, with CTNNB1 levels at the membrane increasing over time, particularly more strongly in the Wnt3a condition. This stronger temporal increase may reflect ongoing membrane-associated signaling activity driven by receptor engagement and clustering that occurs during ligand stimulation. The significant CHIR-induced increase may reflect accumulation of stabilized CTNNB1 at the membrane due to impaired degradation rather than active recruitment via signaling. The membrane signal in both conditions decreases at later time frames, suggesting CTNNB1 relocation to the nucleus after the initial signal propagation through the membrane in Wnt3a condition. For CHIR condition the decrease could be attributed to negative feedback mechanisms, or translocation of built-up CTNNB1 to the nucleus.



Our findings regarding the nuclear-to-cytoplasmic CTNNB1 signal ratios across control, Wnt3 and CHIR conditions in HAP1 cells are in strong agreement with a more extensive study performed by de Man, S. M. A. and colleagues. The cited study, however, did not analyze the changes in membrane CTNNB1 signal across conditions [4].



Overall, this study demonstrates how quantitative image analysis can provide meaningful insight into protein localization dynamics in response to different treatment conditions. By combining optimized segmentation workflows with statistical modeling, we were able to capture both the spatial redistribution of CTNNB1 and the distinct effects of Wnt3a and CHIR treatments compared to the control over time. While methodological limitations remain, particularly regarding statistical analysis and tracking, our pipeline builds a framework for future improvements and highlights the biological relevance of CTNNB1 localization patterns in Wnt signaling pathway.





7. Group Contributions

![](media/Screenshot%202025-06-27%20at%2000.02.35.png)



8. References


[1] Zhang, Y., & Wang, X. (2020). Targeting the Wnt/β‑catenin signaling pathway in cancer. Journal of Hematology & Oncology, 13(165).

[2] Pachitariu, M., Rariden, M., & Stringer, C. (2025). Cellpose‑SAM: superhuman generalization for cellular segmentation. bioRxiv, 2025.04.28.651001.

[3] Allan, D. B., Caswell, T., Keim, N. C., van der Wel, C. M., & Verweij, R. W. (2024). soft-matter/trackpy: v0.6.4 (Version 0.6.4) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.12708864

[4] Schmidt, U., Weigert, M., Broaddus, C., & Myers, G. (2018). Cell detection with star-convex polygons. eLife, 7, e66440.