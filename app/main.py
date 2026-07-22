from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from collections import Counter

from app.database import engine, Base, get_db
from app.models import JobListing
from app.extractor import fetch_and_store_jobs

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Market Analytics & Data Extraction Engine",
    description="Automated Remote Job Aggregator with FastAPI & MySQL Integration",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Job Market Analytics API is running live."}

@app.post("/api/trigger-extraction")
def trigger_extraction(db: Session = Depends(get_db)):
    return fetch_and_store_jobs(db)

@app.get("/api/jobs")
def get_jobs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(JobListing).offset(skip).limit(limit).all()

@app.get("/api/analytics/top-skills")
def get_top_skills(limit: int = 10, db: Session = Depends(get_db)):
    all_jobs = db.query(JobListing.tags).all()
    skill_counter = Counter()

    for (tags,) in all_jobs:
        if tags:
            skills = [s.strip().lower() for s in tags.split(",") if s.strip()]
            skill_counter.update(skills)

    top_skills = [{"skill": skill, "count": count} for skill, count in skill_counter.most_common(limit)]
    return {"top_demanded_skills": top_skills}
