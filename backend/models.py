from pydantic import BaseModel

class UserData(BaseModel):
    weight: float   # kg
    height: float   # feet
    age: int
    gender: str     # male/female
    activity_level: int  # 1,2,3
    goal: str       # lose, maintain, gain
