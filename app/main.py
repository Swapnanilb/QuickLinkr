import string
import random
import qrcode
import io
import base64
import httpx
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from . import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="QuickLinkr API", description="Smart URL shortener with analytics and QR codes")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_qr_code(url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

async def validate_url(url: str) -> bool:
    """Check if URL is reachable"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.head(url, follow_redirects=True)
            return response.status_code < 400
    except:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)
                return response.status_code < 400
        except:
            return False

@app.post("/shorten", response_model=schemas.URLResponse)
async def shorten_url(url_data: schemas.URLCreate, db: Session = Depends(database.get_db)):
    # Validate URL is reachable
    url_str = str(url_data.url)
    is_valid = await validate_url(url_str)
    if not is_valid:
        raise HTTPException(status_code=400, detail="URL is not reachable or invalid")
    
    # Use custom code if provided
    if url_data.custom_code:
        if len(url_data.custom_code) < 3:
            raise HTTPException(status_code=400, detail="Custom code must be at least 3 characters")
        existing = db.query(models.URL).filter(models.URL.short == url_data.custom_code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom code already exists")
        short_code = url_data.custom_code
    else:
        # Generate unique short code
        while True:
            short_code = generate_short_code()
            existing = db.query(models.URL).filter(models.URL.short == short_code).first()
            if not existing:
                break
    
    # Calculate expiration date
    expires_at = None
    if url_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=url_data.expires_in_days)
    
    # Create new URL entry
    db_url = models.URL(original=url_str, short=short_code, expires_at=expires_at)
    db.add(db_url)
    db.commit()
    
    short_url = f"http://localhost:8000/{short_code}"
    qr_code = generate_qr_code(short_url)
    
    return schemas.URLResponse(short_url=short_url, qr_code=qr_code)

@app.get("/{code}")
def redirect_url(code: str, request: Request, db: Session = Depends(database.get_db)):
    db_url = db.query(models.URL).filter(models.URL.short == code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Check if URL has expired
    if db_url.expires_at and datetime.utcnow() > db_url.expires_at:
        raise HTTPException(status_code=410, detail="URL has expired")
    
    # Log click for analytics (with error handling)
    try:
        click_log = models.ClickLog(
            url_id=db_url.id,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else "unknown"
        )
        db.add(click_log)
    except Exception:
        pass  # Continue even if logging fails
    
    # Increment click count
    db_url.clicks += 1
    db.commit()
    
    return RedirectResponse(url=db_url.original)

@app.get("/info/{code}", response_model=schemas.URLInfo)
def get_url_info(code: str, db: Session = Depends(database.get_db)):
    db_url = db.query(models.URL).filter(models.URL.short == code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    return schemas.URLInfo(
        original_url=db_url.original,
        short_code=db_url.short,
        clicks=db_url.clicks
    )

@app.get("/api/history", response_model=List[schemas.URLInfo])
def get_url_history(db: Session = Depends(database.get_db)):
    try:
        urls = db.query(models.URL).order_by(models.URL.id.desc()).limit(10).all()
        return [schemas.URLInfo(
            original_url=url.original,
            short_code=url.short,
            clicks=url.clicks,
            created_at=getattr(url, 'created_at', None),
            expires_at=getattr(url, 'expires_at', None)
        ) for url in urls]
    except Exception:
        # Fallback for old database schema
        from sqlalchemy import text
        urls = db.execute(text("SELECT id, original, short, clicks FROM urls ORDER BY id DESC LIMIT 10")).fetchall()
        return [schemas.URLInfo(
            original_url=url[1],
            short_code=url[2],
            clicks=url[3],
            created_at=None,
            expires_at=None
        ) for url in urls]

@app.delete("/api/history")
def clear_history(db: Session = Depends(database.get_db)):
    db.query(models.ClickLog).delete()
    db.query(models.URL).delete()
    db.commit()
    return {"message": "History cleared successfully"}

@app.get("/api/analytics", response_model=schemas.AnalyticsData)
def get_analytics(db: Session = Depends(database.get_db)):
    try:
        # Basic stats
        total_urls = db.query(models.URL).count()
        total_clicks = db.query(func.sum(models.URL.clicks)).scalar() or 0
        
        # Today's clicks (fallback to URL clicks if ClickLog table doesn't exist)
        today = datetime.utcnow().date()
        try:
            clicks_today = db.query(models.ClickLog).filter(
                func.date(models.ClickLog.clicked_at) == today
            ).count()
        except Exception:
            clicks_today = 0
        
        # This week's clicks
        try:
            week_ago = datetime.utcnow() - timedelta(days=7)
            clicks_this_week = db.query(models.ClickLog).filter(
                models.ClickLog.clicked_at >= week_ago
            ).count()
        except Exception:
            clicks_this_week = 0
        
        # Top URLs
        top_urls = db.query(models.URL).order_by(models.URL.clicks.desc()).limit(5).all()
        top_urls_data = [{
            "short_code": url.short,
            "clicks": url.clicks,
            "original_url": url.original[:50] + "..." if len(url.original) > 50 else url.original
        } for url in top_urls]
        
        # Daily clicks for last 7 days (simplified)
        daily_clicks = []
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            daily_clicks.append({
                "date": date.strftime("%Y-%m-%d"),
                "clicks": 0  # Simplified for now
            })
        
        return schemas.AnalyticsData(
            total_urls=total_urls,
            total_clicks=total_clicks,
            clicks_today=clicks_today,
            clicks_this_week=clicks_this_week,
            top_urls=top_urls_data,
            daily_clicks=list(reversed(daily_clicks))
        )
    except Exception as e:
        # Fallback response
        return schemas.AnalyticsData(
            total_urls=0,
            total_clicks=0,
            clicks_today=0,
            clicks_this_week=0,
            top_urls=[],
            daily_clicks=[{"date": datetime.utcnow().strftime("%Y-%m-%d"), "clicks": 0}]
        )

@app.post("/bulk-shorten", response_model=schemas.BulkURLResponse)
async def bulk_shorten_urls(url_data: schemas.BulkURLCreate, db: Session = Depends(database.get_db)):
    results = []
    for url_str in url_data.urls:
        try:
            # Validate URL first
            is_valid = await validate_url(url_str)
            if not is_valid:
                continue
                
            # Generate unique short code
            while True:
                short_code = generate_short_code()
                existing = db.query(models.URL).filter(models.URL.short == short_code).first()
                if not existing:
                    break
            
            # Create new URL entry
            db_url = models.URL(original=url_str, short=short_code)
            db.add(db_url)
            db.commit()
            
            short_url = f"http://localhost:8000/{short_code}"
            qr_code = generate_qr_code(short_url)
            
            results.append(schemas.URLResponse(short_url=short_url, qr_code=qr_code))
        except Exception:
            continue
    
    return schemas.BulkURLResponse(results=results)

@app.post("/bulk-upload")
async def bulk_upload(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    content = await file.read()
    urls = content.decode().strip().split('\n')
    
    results = []
    for url_str in urls:
        url_str = url_str.strip()
        if url_str and url_str.startswith('http'):
            try:
                # Validate URL first
                is_valid = await validate_url(url_str)
                if not is_valid:
                    continue
                    
                while True:
                    short_code = generate_short_code()
                    existing = db.query(models.URL).filter(models.URL.short == short_code).first()
                    if not existing:
                        break
                
                db_url = models.URL(original=url_str, short=short_code)
                db.add(db_url)
                db.commit()
                
                short_url = f"http://localhost:8000/{short_code}"
                qr_code = generate_qr_code(short_url)
                
                results.append({"original": url_str, "short_url": short_url, "qr_code": qr_code})
            except Exception:
                continue
    
    return {"message": f"Processed {len(results)} URLs", "results": results}