import json
import DiffRes as d
import scripts.BasicChange as bc
from dataclasses import asdict, is_dataclass
from enum import Enum
from abc import ABC, abstractmethod

class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"

class DiffResRenderer(ABC):

    @abstractmethod
    def render(self, dr : d.DiffRes): 
        pass

class JsonDiffRenderer(DiffResRenderer):
    def render(self, dr : d.DiffRes) -> str:
        pass

class HTMLDiffRenderer(DiffResRenderer):
    def render(self, dr: d.DiffRes) -> str:
        pass
    
class TableDiffRenderer(DiffResRenderer):
    def render(self, dr: d.DiffRes) -> str:
        pass