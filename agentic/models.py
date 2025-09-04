import pandas as pd
from pydantic import BaseModel, ConfigDict
from typing import List

class DataFrameWrapper(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    df: pd.DataFrame

class Question(BaseModel):
    slug: str
    topics: List[str]
    difficulty: str


class Questions(BaseModel):
    questions: List[Question]