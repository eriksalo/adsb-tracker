import uvicorn
from loguru import logger

from adsb_tracker.app import create_app
from adsb_tracker.config import Settings


def main() -> None:
    settings = Settings()
    app = create_app(settings)
    logger.info(f"ADS-B Tracker starting at http://{settings.web_host}:{settings.web_port}")
    uvicorn.run(app, host=settings.web_host, port=settings.web_port, log_level="info")


if __name__ == "__main__":
    main()
