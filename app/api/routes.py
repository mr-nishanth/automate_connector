"""Root and health routes."""

from fastapi import APIRouter

from app.schemas import HealthResponse, WelcomeResponse

router = APIRouter()


@router.get("/", response_model=WelcomeResponse)
def root() -> WelcomeResponse:
    return WelcomeResponse(message="Welcome to the automate-connector API")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
