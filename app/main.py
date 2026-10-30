from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

from app.config import settings
from app.schemas.events import EventRequest
from app.tools.weather import get_event_weather


app = FastAPI(
    title="Weather & Calendar Assistant",
    description="An AI assistant that checks weather before scheduling events.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class WeatherRequest(BaseModel):
    location: str = Field(min_length=1, max_length=120)

@app.get("/")
async def root():
    return {
        "message": "Weather & Calendar Assistant API",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/weather")
async def weather_endpoint(request: WeatherRequest):
    try:
        return await get_forecast(request.location)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="The weather service is temporarily unavailable.",
        )


@app.post("/api/event-weather")
async def event_weather_endpoint(request: EventRequest):

    try:
        result = await get_event_weather(
            location=request.location,
            event_date=request.event_date,
            start_time=request.start_time,
            end_time=request.end_time,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Weather API is temporarily unavailable.",
        )