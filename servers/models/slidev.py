from typing import Optional, Union, List, Dict
from pydantic import BaseModel


class SlidevResult(BaseModel):
    success: bool
    message: str
    output: Optional[Union[str, int, List[str]]] = None


class OutlineItem(BaseModel):
    group: str
    content: str


class SaveOutlineParam(BaseModel):
    outlines: List[OutlineItem]