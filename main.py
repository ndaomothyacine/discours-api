from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import random
import logging

logging.basicConfig(level=logging.DEBUG)

import models, schemas
from database import engine, get_db

try:
    models.Base.metadata.create_all(bind=engine)
    logging.info("Tables créées avec succès")
except Exception as e:
    logging.error(f"Erreur création tables: {e}")

app = FastAPI(title="Discours API", description="API pour la bibliothèque de discours")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── THÈMES ───────────────────────────────────────────

@app.post("/themes/", response_model=schemas.Theme)
def creer_theme(theme: schemas.ThemeCreate, db: Session = Depends(get_db)):
    db_theme = models.Theme(**theme.model_dump())
    db.add(db_theme)
    db.commit()
    db.refresh(db_theme)
    return db_theme

@app.get("/themes/", response_model=List[schemas.Theme])
def lister_themes(db: Session = Depends(get_db)):
    return db.query(models.Theme).all()

# ─── DISCOURS ─────────────────────────────────────────

@app.post("/discours/", response_model=schemas.Discours)
def creer_discours(discours: schemas.DiscoursCreate, db: Session = Depends(get_db)):
    data = discours.model_dump(exclude={"theme_ids"})
    db_discours = models.Discours(**data)
    if discours.theme_ids:
        themes = db.query(models.Theme).filter(models.Theme.id.in_(discours.theme_ids)).all()
        db_discours.themes = themes
    db.add(db_discours)
    db.commit()
    db.refresh(db_discours)
    return db_discours

@app.get("/discours/", response_model=List[schemas.Discours])
def lister_discours(
    db: Session = Depends(get_db),
    theme: Optional[str] = Query(None),
    intervenant: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    recherche: Optional[str] = Query(None)
):
    query = db.query(models.Discours)
    if theme:
        query = query.filter(models.Discours.themes.any(nom=theme))
    if intervenant:
        query = query.filter(models.Discours.intervenant.contains(intervenant))
    if format:
        query = query.filter(models.Discours.format == format)
    if recherche:
        query = query.filter(models.Discours.titre.contains(recherche))
    return query.all()

@app.get("/discours/du-jour/", response_model=schemas.Discours)
def discours_du_jour(db: Session = Depends(get_db)):
    tous = db.query(models.Discours).all()
    if not tous:
        raise HTTPException(status_code=404, detail="Aucun discours disponible")
    return random.choice(tous)

@app.get("/discours/{discours_id}", response_model=schemas.Discours)
def obtenir_discours(discours_id: int, db: Session = Depends(get_db)):
    discours = db.query(models.Discours).filter(models.Discours.id == discours_id).first()
    if not discours:
        raise HTTPException(status_code=404, detail="Discours introuvable")
    return discours

@app.put("/discours/{discours_id}/favori", response_model=schemas.Discours)
def toggle_favori(discours_id: int, db: Session = Depends(get_db)):
    discours = db.query(models.Discours).filter(models.Discours.id == discours_id).first()
    if not discours:
        raise HTTPException(status_code=404, detail="Discours introuvable")
    discours.est_favori = 0 if discours.est_favori else 1
    db.commit()
    db.refresh(discours)
    return discours

@app.get("/favoris/", response_model=List[schemas.Discours])
def lister_favoris(db: Session = Depends(get_db)):
    return db.query(models.Discours).filter(models.Discours.est_favori == 1).all()

@app.delete("/discours/{discours_id}")
def supprimer_discours(discours_id: int, db: Session = Depends(get_db)):
    discours = db.query(models.Discours).filter(models.Discours.id == discours_id).first()
    if not discours:
        raise HTTPException(status_code=404, detail="Discours introuvable")
    db.delete(discours)
    db.commit()
    return {"message": "Discours supprimé"}