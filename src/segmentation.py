from cellpose import models

def segment_nuclei(image, diameter=30):
    # cellpose model for nuclei
    model = models.Cellpose(model_type='nuclei')
    
    masks, flows, styles, diams = model.eval(image, diameter=diameter, channels=[0,0])
    
    return masks

def segment_cells(image, diameter=80):

    # cellpose model for cells
    model = models.Cellpose(model_type='cyto2')
    
    masks, flows, styles, diams = model.eval(image, diameter=diameter, channels=[0,0])
    
    return masks 


def cpsam_segmentation(image, diameter):
    # latest general cellpose model for segmentation 
    model = models.CellposeModel(gpu=True)

    masks, flows, styles = model.eval(image, diameter=diameter, channels=[0,0])

    return masks