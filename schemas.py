from pydantic import BaseModel
from typing import Optional, List

class ThemeBase(BaseModel):
    nom: str
    description: Optional[str] = None

class ThemeCreate(ThemeBase):
    pass

class Theme(ThemeBase):
    id: int

    class Config:
        from_attributes = True

class DiscoursBase(BaseModel):
    titre: str
    intervenant: str
    format: str
    description: Optional[str] = None
    fichier_url: Optional[str] = None
    date: Optional[str] = None
class DiscoursCreate(DiscoursBase):
    theme_ids: Optional[List[int]] = []

class Discours(DiscoursBase):
    id: int
    est_favori: int
    themes: List[Theme] = []

    class Config:
        from_attributes = True