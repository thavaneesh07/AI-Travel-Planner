import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def test_imports():
    from backend.config import settings
    from backend.loggingconfig import setup_logging
    from backend.database.base import Base
    from backend.database.session import engine, get_db
    from backend.utils.retry import with_retry
    from backend.auth.jwthandler import create_access_token, decode_access_token
    from backend.auth.password import get_password_hash, verify_password
    from backend.auth.guards import check_trip_ownership
    from backend.cache.redisclient import RedisCache
    from backend.ai.promptregistry import PROMPTS
    from backend.ai.ollamaclient import OllamaClient
    from backend.ai.intentengine import TravelIntentEngine
    from backend.ai.structuredparser import clean_extracted_entities
    from backend.agents.travelassistantagent import TravelAssistantAgent
    from backend.agents.tripplanningagent import TripPlanningAgent
    from backend.services.maps.geocoding import GeocodingService
    from backend.services.maps.places import PlacesService
    from backend.services.maps.routing import RoutingService
    from backend.services.weather.weatherservice import WeatherService
    from backend.services.budget.budgetscorer import BudgetScorer
    from backend.services.routeoptimizer.optimizer import RouteOptimizer
    from backend.services.itinerary.generator import ItineraryGenerator
    from backend.services.itinerary.editor import ItineraryEditor
    from backend.services.export.pdf_exporter import PdfExporter
    from backend.routers.authrouter import router as r1
    from backend.routers.triprouter import router as r2
    from backend.routers.generaterouter import router as r3
    from backend.main import app

    print("All backend modules imported successfully!")

if __name__ == "__main__":
    test_imports()
