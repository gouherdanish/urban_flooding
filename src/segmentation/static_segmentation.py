from typing import Union
from pathlib import Path
import geopandas as gpd

from segmentation.base_segmentation import BaseSegmentation

class StaticSegmentation(BaseSegmentation):
    def __init__(self, file_path:Union[Path,str]) -> None:
        self.file_path = file_path

    def segment(self):
        df = gpd.read_file(self.file_path)
        df['x'] = df['geometry'].x
        df['y'] = df['geometry'].y
        return df