from pydantic import BaseModel


class DatabaseCredentials(BaseModel):
    driver_name: str
    host: str
    port: int
    database: str
    user: str
    password: str
    extras: dict = {}
