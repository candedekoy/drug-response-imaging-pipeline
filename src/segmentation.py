from cellpose import models

def segment_nuclei(image, diameter=30):
    # cellpose model for nuclei
    model = models.Cellpose(model_type='nuclei')
    
    # running the model
    masks, flows, styles, diams = model.eval(image, diameter=diameter, channels=[0,0])
    
    return masks

def segment_cells(image, diameter=80):

    # cellpose model for cells
    model = models.Cellpose(model_type='cyto2')
    
    # running the model
    masks, flows, styles, diams = model.eval(image, diameter=diameter, channels=[0,0])
    
    return masks 