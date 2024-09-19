from typing import Union
from pathlib import Path
import pandas as pd

from segmentation.base_segmentation import BaseSegmentation

class StaticSegmentation(BaseSegmentation):
    def __init__(self, file_path:Union[Path,str]) -> None:
        self.file_path = file_path

    def segment(self):
        return pd.read_csv(self.file_path)