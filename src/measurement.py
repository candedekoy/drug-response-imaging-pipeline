import numpy as np
import pandas as pd
from skimage.measure import regionprops_table

def measure_intensities(nuc_mask, cyto_mask, mem_mask, nuc_signal, cell_signal):
    """
    measures the mean intensity in the nucleus, cytoplasm, and membrane for each cell.

    """

    # measuring nucleus intensity
    nuc_props = regionprops_table(
        nuc_mask,
        intensity_image=nuc_signal,
        properties=('label', 'mean_intensity')
    )
    df_nuc = pd.DataFrame(nuc_props).rename(columns={'mean_intensity': 'nuc_mean_intensity'})

    # measuring cytoplasm intensity
    cyto_props = regionprops_table(
        cyto_mask,
        intensity_image=cell_signal,
        properties=('label', 'mean_intensity')
    )
    df_cyto = pd.DataFrame(cyto_props).rename(columns={'mean_intensity': 'cyto_mean_intensity'})

    # measuring membrane intensity
    mem_props = regionprops_table(
        mem_mask,
        intensity_image=cell_signal,
        properties=('label', 'mean_intensity')
    )
    df_mem = pd.DataFrame(mem_props).rename(columns={'mean_intensity': 'mem_mean_intensity'})

    # merging the dataframes
    df = pd.merge(df_nuc, df_cyto, on='label', how='outer')
    df = pd.merge(df, df_mem, on='label', how='outer')

    return df 