from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple
import time

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
    position: Tuple[float, float]  # (x, y) = (longitude, latitude)
    theta: float
    last_update: datetime
    connect_timestamp: float = field(default_factory=time.time)
    current_order: Optional[str] = None
    errors: List[ErrorInfo] = field(default_factory=list)
