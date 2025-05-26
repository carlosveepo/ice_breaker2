from typing import List, Dict, Any, Optional
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Product(BaseModel):
    Product: str
    Price: str
    Benefit: List[str]
    Marketing_Blurb: Optional[str] = Field(alias="Marketing Blurb")

class Summary(BaseModel):
    summary: str = Field(description="summary")
    products: List[Product] = Field(description="List of product objects")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "ProductList": [p.model_dump(by_alias=True) for p in self.products]
        }

summary_parser = PydanticOutputParser(pydantic_object=Summary)
