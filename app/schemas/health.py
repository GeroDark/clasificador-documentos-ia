from pydantic import BaseModel


class HealthComponentResponse(BaseModel):
    ok: bool
    detail: str


class HealthReadyResponse(BaseModel):
    status: str
    database: HealthComponentResponse
    redis: HealthComponentResponse