from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    message: str
    csv_url: str

class ChartConfig(BaseModel):
    type: str # "bar", "line", "pie", "area"
    title: str
    data: List[Dict[str, Any]]
    xKey: str
    yKey: str
    xLabel: Optional[str] = None
    yLabel: Optional[str] = None

class ChatResponse(BaseModel):
    text: str
    charts: List[ChartConfig] = []
