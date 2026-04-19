from pydantic import BaseModel


class CurrentWeather(BaseModel):
    last_updated: str
    temp_c: float
    temp_f: float
    condition: str
