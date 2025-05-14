from pydantic import BaseModel, ConfigDict
from pydantic_mongo import ObjectIdField
from typing import Optional

class BookModel(BaseModel):
    id: Optional[ObjectIdField] = None
    title: str
    author: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectIdField: str}
    )
