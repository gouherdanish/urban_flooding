from abc import ABC, abstractmethod

class BaseSegmentation(ABC):
    @abstractmethod
    def segment(self):
        pass
