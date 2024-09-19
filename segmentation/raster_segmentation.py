from typing import Union, List
from pathlib import Path
import rioxarray
import numpy as np
import pandas as pd
import geopandas as gpd

from segmentation.base_segmentation import BaseSegmentation

class RasterSegmentation(BaseSegmentation):
    def __init__(self, dtm_path:Union[Path,str]) -> None:
        self.xda = rioxarray.open_rasterio(dtm_path)
        self.dtm = self.xda.data[0]

    def _heights_of_neighbor_pixels(self,*pixel):
        i,j = pixel
        return self.dtm[(max(i-1,0),max(j-1,0))],self.dtm[(max(i-1,0),j)],self.dtm[(max(i-1,0),min(j+1,n-1))],self.dtm[(i,max(j-1,0))],self.dtm[(i,min(j+1,n-1))],self.dtm[(min(i+1,m-1),max(j-1,0))],self.dtm[(min(i+1,m-1),max(j-1,0))],self.dtm[(min(i+1,m-1),min(j+1,n-1))]

    def _classify_pixel(self,*pixel):
        height_of_this_pixel = self.dtm[pixel]
        return 1 if height_of_this_pixel < min(self._heights_of_neighbor_pixels(pixel)) else 0
    
    def segment(self):
        m,n = self.dtm.shape
        segmented = np.zeros(m,n)
        for i in range(m):
            for j in range(n):
                segmented[i,j] = self.classify(i,j)
        x = self.xda.x.values
        y = self.xda.y.values
        x, y = np.meshgrid(x, y)
        x, y, segmented = x.flatten(), y.flatten(), segmented.flatten()
        df_seg = pd.DataFrame.from_dict({'label': segmented, 'x': x, 'y': y})
        df_target = df_seg[df_seg.label == 1].reset_index(drop=True)
        return df_target

