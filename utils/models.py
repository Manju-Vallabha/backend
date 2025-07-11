from pydantic import BaseModel


class fileAccessPayload(BaseModel):
    # Define fields for file access
    role: str
    email: str


class DetailsPayload(BaseModel):
    # Define fields common for both certificate and badge
    name: str
    email: str


class fileAccessPayload(BaseModel):
    # Define fields for file access
    role: str
    email: str


class loginPayload(BaseModel):
    # Define fields for login
    email: str
