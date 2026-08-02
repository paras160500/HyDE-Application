#==========================================================================================
#                                   Import Statements
#==========================================================================================

from pydantic import BaseModel
from typing import Optional 

#==========================================================================================
#                                   Class Statements
#==========================================================================================

class QueryRequest(BaseModel):
    query : str 
    top_k : Optional[int] = 5 
    namespace : Optional[str] = ""

class CompareRequest(BaseModel):
    query : str 
    top_k : Optional[int] = 5 
    namespace : Optional[str] = ""

class IngestRequest(BaseModel):
    documents : list[dict]  # [{"id" : "..." , "text" : "..." , "metadata" : {...} }]
    namespace : Optional[str] = ""