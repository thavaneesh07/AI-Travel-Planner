from abc import ABC, abstractmethod
from typing import Dict, Any

class ExportAdapter(ABC):
    @abstractmethod
    def export(self, trip_data: Dict[str, Any], output_path: str) -> str:
        pass
