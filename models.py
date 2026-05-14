from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

discours_themes = Table(
    "discours_themes",
    Base.metadata,
    Column("discours_id", Integer, ForeignKey("discours.id")),
    Column("theme_id", Integer, ForeignKey("themes.id"))
)

class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    discours = relationship("Discours", secondary=discours_themes, back_populates="themes")

class Discours(Base):
    __tablename__ = "discours"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    intervenant = Column(String, nullable=False)
    format = Column(String, nullable=False)
    date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    fichier_url = Column(String, nullable=True)
    est_favori = Column(Integer, default=0)
    themes = relationship("Theme", secondary=discours_themes, back_populates="discours")