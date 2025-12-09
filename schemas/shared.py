from pydantic import BaseModel, model_validator
from typing import Any, Dict

class TrimmedBaseModel(BaseModel):
    @model_validator(mode='before')
    def trim_strings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v.strip() if isinstance(v, str) else v for k, v in values.items()}
