import requests
from sqlalchemy.orm import Session
from app.models import JobListing

REMOTEOK_API_URL = "https://remoteok.com/api"

def fetch_and_store_jobs(db: Session):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(REMOTEOK_API_URL, headers=headers)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch remote jobs"}
    
    data = response.json()
    saved_count = 0

    for item in data[1:]:
        if not isinstance(item, dict):
            continue
            
        job_id = str(item.get("id"))
        if not job_id:
            continue

        existing_job = db.query(JobListing).filter(JobListing.job_id == job_id).first()
        if not existing_job:
            tags_list = item.get("tags", [])
            tags_str = ",".join(tags_list) if isinstance(tags_list, list) else ""

            job = JobListing(
                job_id=job_id,
                title=item.get("position", "N/A"),
                company=item.get("company", "N/A"),
                location=item.get("location", "Remote"),
                tags=tags_str,
                url=item.get("url", "")
            )
            db.add(job)
            saved_count += 1

    db.commit()
    return {"status": "success", "new_jobs_added": saved_count}
