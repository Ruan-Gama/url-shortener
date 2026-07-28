"""
Schemas Pydantic usados para validação de entrada e serialização de saída
da API (request/response models).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class URLCreate(BaseModel):
    """Payload esperado para criar uma nova URL encurtada."""

    original_url: HttpUrl


class URLResponse(BaseModel):
    """Formato de resposta devolvido pela API para uma URL encurtada."""

    id: int
    original_url: str
    short_code: str
    clicks: int
    created_at: datetime

    # Permite construir o schema diretamente a partir de um objeto ORM
    # (models.URL), sem precisar converter manualmente para dict.
    model_config = ConfigDict(from_attributes=True)