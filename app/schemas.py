from pydantic import BaseModel, ConfigDict


class URLCreate(BaseModel):
    original_url: str


class URLResponse(BaseModel):
    original_url: str
    short_code: str

    # Permite retornar objeto do SQLAlchemy direto
    model_config = ConfigDict(from_attributes=True)