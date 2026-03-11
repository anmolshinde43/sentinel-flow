from pydantic import BaseModel

class EmployeeCreate(BaseModel):
    name: str
    email: str
    role: str
    salary: int