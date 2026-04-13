from pydantic import BaseModel


class ValidationErrorDetail(BaseModel):
    loc: list[str]
    message: str
    type: str


class ApiErrorResponse(BaseModel):
    code: str
    message: str
    details: list[ValidationErrorDetail] | None = None
