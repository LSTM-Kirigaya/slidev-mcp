from typing import Optional, Union, List, Dict
from pydantic import BaseModel


class SlidevResult(BaseModel):
    success: bool
    message: str
    data: Optional[Union[str, int, List[str]]] = None


class OutlineItem(BaseModel):
    group: str
    content: str


class SaveOutlineParam(BaseModel):
    outlines: List[OutlineItem]


class SlidevCreateParam(BaseModel):
    name: str


class SlidevLoadParam(BaseModel):
    name: str


class SlidevMakeCoverParam(BaseModel):
    title: str
    subtitle: Optional[str] = ""
    author: Optional[str] = ""
    authorUrl: Optional[str] = ""
    backgroundUrl: Optional[str] = ""


class SlidevAddPageParam(BaseModel):
    content: str
    layout: str = "default"
    parameters: Optional[Dict] = {}


class SlidevSetPageParam(BaseModel):
    index: int
    content: str
    layout: Optional[str] = ""
    parameters: Optional[Dict] = {}


class SlidevGetPageParam(BaseModel):
    index: int