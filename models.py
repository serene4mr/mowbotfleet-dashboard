from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

@dataclass
class ErrorInfo:
    timestamp: datetime
    type: str
    description: str
    severity: str

@dataclass
class AGVInfo:
    serial: str
    manufacturer: str
    connection: str
    battery: float
    operating_mode: str
    position: Tuple[float, float]
    theta: float
    last_update: datetime
    current_order: Optional[str] = None
    errors: List[ErrorInfo] = field(default_factory=list)
