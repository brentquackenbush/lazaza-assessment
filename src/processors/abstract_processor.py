from abc import ABC, abstractmethod

class AbstractProcessor(ABC):
    @abstractmethod
    def process(self):
        pass
