from pydantic import BaseModel
from typing import List

class URLRequest(BaseModel):
    url: str

class URLResponse(BaseModel):
    url: str
    isMalicious: bool

class CSVResult(BaseModel):
    url: str
    isMalicious: bool

class CSVResponse(BaseModel):
    results: List[CSVResult]
