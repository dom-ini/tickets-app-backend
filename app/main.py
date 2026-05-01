from app.app_factory import create_app
from app.core.config import settings

app = create_app(settings)
