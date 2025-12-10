# resource_catalog_service/app.py
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
import geopy.distance
from geopy.geocoders import Nominatim

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resource Catalog Service")

# Database setup
DATABASE_URL = "postgresql://user:password@localhost/resource_catalog_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis for caching
redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

class HealthcareProvider(Base):
    __tablename__ = "healthcare_providers"
    
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    specialty = Column(String)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String)
    website = Column(String)
    accepts_insurance = Column(Boolean, default=True)
    languages = Column(Text)  # JSON array
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CommunityResource(Base):
    __tablename__ = "community_resources"
    
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    type = Column(String)  # support_group, education, transportation, etc.
    description = Column(Text)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    contact_info = Column(Text)
    hours = Column(Text)  # JSON object
    eligibility = Column(Text)  # JSON array
    languages = Column(Text)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResourceSearchRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    specialty: Optional[str] = None
    resource_type: Optional[str] = None
    max_distance: Optional[float] = 25.0  # miles
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class ProviderResponse(BaseModel):
    id: str
    name: str
    specialty: str
    address: str
    city: str
    state: str
    zip_code: str
    distance: Optional[float] = None
    phone: str
    website: Optional[str]
    accepts_insurance: bool
    languages: List[str]
    rating: float
    review_count: int

class CommunityResourceResponse(BaseModel):
    id: str
    name: str
    type: str
    description: str
    address: str
    city: str
    state: str
    zip_code: str
    distance: Optional[float] = None
    contact_info: str
    hours: Dict[str, str]
    eligibility: List[str]
    languages: List[str]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in miles"""
    return geopy.distance.distance((lat1, lon1), (lat2, lon2)).miles

@app.get("/v1/providers/search", response_model=List[ProviderResponse])
async def search_providers(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    specialty: Optional[str] = Query(None),
    max_distance: Optional[float] = Query(25.0),
    limit: Optional[int] = Query(20),
    offset: Optional[int] = Query(0),
    db = Depends(get_db)
):
    """Search for healthcare providers"""
    try:
        # Check cache first
        cache_key = f"providers:{latitude}:{longitude}:{specialty}:{max_distance}:{limit}:{offset}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Build query
        query = db.query(HealthcareProvider)
        
        if specialty:
            query = query.filter(HealthcareProvider.specialty.ilike(f"%{specialty}%"))
        
        # Apply location-based filtering
        providers = query.offset(offset).limit(limit).all()
        
        # Calculate distances and filter by max_distance
        results = []
        for provider in providers:
            provider_dict = {
                "id": provider.id,
                "name": provider.name,
                "specialty": provider.specialty,
                "address": provider.address,
                "city": provider.city,
                "state": provider.state,
                "zip_code": provider.zip_code,
                "phone": provider.phone,
                "website": provider.website,
                "accepts_insurance": provider.accepts_insurance,
                "languages": json.loads(provider.languages) if provider.languages else [],
                "rating": provider.rating,
                "review_count": provider.review_count
            }
            
            if latitude is not None and longitude is not None and provider.latitude and provider.longitude:
                distance = calculate_distance(latitude, longitude, provider.latitude, provider.longitude)
                if distance <= max_distance:
                    provider_dict["distance"] = round(distance, 2)
                    results.append(ProviderResponse(**provider_dict))
            else:
                results.append(ProviderResponse(**provider_dict))
        
        # Sort by distance if location provided
        if latitude is not None and longitude is not None:
            results.sort(key=lambda x: x.distance or float('inf'))
        
        # Cache result for 30 minutes
        redis_client.setex(cache_key, 1800, json.dumps([r.dict() for r in results]))
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search providers")

@app.get("/v1/resources/search", response_model=List[CommunityResourceResponse])
async def search_community_resources(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    resource_type: Optional[str] = Query(None),
    max_distance: Optional[float] = Query(25.0),
    limit: Optional[int] = Query(20),
    offset: Optional[int] = Query(0),
    db = Depends(get_db)
):
    """Search for community resources"""
    try:
        # Check cache first
        cache_key = f"resources:{latitude}:{longitude}:{resource_type}:{max_distance}:{limit}:{offset}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Build query
        query = db.query(CommunityResource)
        
        if resource_type:
            query = query.filter(CommunityResource.type.ilike(f"%{resource_type}%"))
        
        # Apply pagination
        resources = query.offset(offset).limit(limit).all()
        
        # Calculate distances and filter by max_distance
        results = []
        for resource in resources:
            resource_dict = {
                "id": resource.id,
                "name": resource.name,
                "type": resource.type,
                "description": resource.description,
                "address": resource.address,
                "city": resource.city,
                "state": resource.state,
                "zip_code": resource.zip_code,
                "contact_info": resource.contact_info,
                "hours": json.loads(resource.hours) if resource.hours else {},
                "eligibility": json.loads(resource.eligibility) if resource.eligibility else [],
                "languages": json.loads(resource.languages) if resource.languages else []
            }
            
            if latitude is not None and longitude is not None and resource.latitude and resource.longitude:
                distance = calculate_distance(latitude, longitude, resource.latitude, resource.longitude)
                if distance <= max_distance:
                    resource_dict["distance"] = round(distance, 2)
                    results.append(CommunityResourceResponse(**resource_dict))
            else:
                results.append(CommunityResourceResponse(**resource_dict))
        
        # Sort by distance if location provided
        if latitude is not None and longitude is not None:
            results.sort(key=lambda x: x.distance or float('inf'))
        
        # Cache result for 30 minutes
        redis_client.setex(cache_key, 1800, json.dumps([r.dict() for r in results]))
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching community resources: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search community resources")

@app.get("/v1/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: str, db = Depends(get_db)):
    """Get detailed information about a specific healthcare provider"""
    try:
        # Check cache first
        cache_key = f"provider:{provider_id}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        provider = db.query(HealthcareProvider).filter(HealthcareProvider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        result = ProviderResponse(
            id=provider.id,
            name=provider.name,
            specialty=provider.specialty,
            address=provider.address,
            city=provider.city,
            state=provider.state,
            zip_code=provider.zip_code,
            phone=provider.phone,
            website=provider.website,
            accepts_insurance=provider.accepts_insurance,
            languages=json.loads(provider.languages) if provider.languages else [],
            rating=provider.rating,
            review_count=provider.review_count
        )
        
        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(result.dict()))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving provider: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve provider")

@app.get("/v1/resources/{resource_id}", response_model=CommunityResourceResponse)
async def get_community_resource(resource_id: str, db = Depends(get_db)):
    """Get detailed information about a specific community resource"""
    try:
        # Check cache first
        cache_key = f"resource:{resource_id}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        resource = db.query(CommunityResource).filter(CommunityResource.id == resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        result = CommunityResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            description=resource.description,
            address=resource.address,
            city=resource.city,
            state=resource.state,
            zip_code=resource.zip_code,
            contact_info=resource.contact_info,
            hours=json.loads(resource.hours) if resource.hours else {},
            eligibility=json.loads(resource.eligibility) if resource.eligibility else [],
            languages=json.loads(resource.languages) if resource.languages else []
        )
        
        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(result.dict()))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving community resource: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve community resource")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Initialize database
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
