from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    dump1090_host: str = "127.0.0.1"
    dump1090_sbs_port: int = 30003
    dump1090_beast_port: int = 30005

    web_host: str = "0.0.0.0"
    web_port: int = 8080

    station_lat: float | None = None
    station_lon: float | None = None

    aircraft_ttl_seconds: int = 60

    radarbox_enabled: bool = False
    radarbox_host: str = "feed.radarbox.com"
    radarbox_port: int = 30005

    tar1090_path: str = ""
