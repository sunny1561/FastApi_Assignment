# from typing import Dict, List, Optional,Any
# from bson import ObjectId
# from fastapi import FastAPI, HTTPException, Path, Query, Body
# from pydantic import BaseModel
# from pymongo import MongoClient

# app = FastAPI()

# # Connect to MongoDB remotely
# client = MongoClient("mongodb+srv://sunnykumar:sunny450@cluster0.nggkwbc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# db = client["Cosmocloud"]
# student_collection = db["student"]

# @app.get("/")
# async def root():
#     return {"message2": "Welcome to the Library Management System by Sunny Kumar!"}  
  

# class Address(BaseModel):
#     city: str
#     country: str

# class Student(BaseModel):
#     name: Optional[str]  # Make the name field optional
#     age: Optional[int]
#     address: Optional[Address]

# # Create student
# @app.post("/students", response_model=Dict[str, str])
# async def create_student(student: Student):
#     student_dict = student.dict()
#     result = student_collection.insert_one(student_dict)
#     return {"id": str(result.inserted_id)}

# # List of students
# @app.get("/students", response_model=List[Student])
# async def list_students(country: str = Query(None), age: int = None):
#     query = {}
#     if country:
#         query["address.country"] = country
#     if age:
#         query["age"] = {"$gte": age}
#     students = list(student_collection.find(query))
#     return students


# @app.patch("/students/{id}", response_model=Dict[str, str])
# async def update_student(id: str = Path(...), student_update: Dict[str, Any] = Body(...)):
#     result = student_collection.update_one({"_id": ObjectId(id)}, {"$set": student_update})
#     if result.modified_count == 1:
#         return {"message": "Student updated successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Student not found")   

# # Fetch student with id
# @app.get("/students/{id}", response_model=Student)
# async def fetch_student(id: str = Path(...)):
#     student = student_collection.find_one({"_id": ObjectId(id)})
#     if student:
#         return student
#     else:
#         raise HTTPException(status_code=404, detail="Student not found")

# # Delete student given id
# @app.delete("/students/{id}", response_model=Dict[str, str])
# async def delete_student(id: str = Path(...)):
#     result = student_collection.delete_one({"_id": ObjectId(id)})
#     if result.deleted_count == 1:
#         return {"message": "Student deleted successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Student not found")

# #doc_dummy=[

# #     {
# #         "name": "sde",
# #         "age": 22,
# #         "address": {"city": "London", "country": "UK"}
# #     },
# #     {
# #         "name": "datasientist",
# #         "age": 25,
# #         "address": {"city": "Paris", "country": "France"}
# #     },
#     # {
#     #     "name": "MLengineer",
#     #     "age": 21,
#     #     "address": {"city": "Berlin", "country": "Germany"}
#     # },
# #     {
# #         "name": "fullstack",
# #         "age": 23,
# #         "address": {"city": "Tokyo", "country": "Japan"}
# #     }
# # ]
# # ##just to see whether database updated or not
# # for json in doc_dummy:
# #     student_collection.insert_one(json)


# #to run fastapi application use below command
# # uvicorn main:app --reload


#below is newly updated(24/4/2024)
from typing import Dict, List, Optional, Any
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Path, Query, Body, Header, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timedelta
import redis
app = FastAPI()
# Connect to MongoDB remotely
client = MongoClient("mongodb+srv://sunnykumar:sunny450@cluster0.nggkwbc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Cosmocloud"]
student_collection = db["student"]

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Maximum requests per day
MAX_REQUESTS_PER_DAY = 500

# Rate limiter function
class RateLimiter:
    @classmethod
    def Rate_limiter(cls, user_id: Optional[str] = Header(None)):
        if user_id is None:
            raise HTTPException(status_code=401, detail="User ID is required")
    
        current_date = datetime.now().date()
        key = f"rate_limit:{user_id}:{current_date}"
        
        # Get the current number of requests for the user and the current date
        current_requests = redis_client.get(key)
        if current_requests is None:
            # If the key doesn't exist, initialize it to 1
            redis_client.set(key, 1, ex=int(timedelta(days=1).total_seconds()))  # Convert to int here
            current_requests = 1
        else:
            current_requests = int(current_requests)
            
            # Check if the rate limit has been exceeded
            if current_requests >= MAX_REQUESTS_PER_DAY:
                raise HTTPException(status_code=429, detail="Too many requests")
            
            # Increment the request count
            redis_client.incr(key)
            current_requests += 1
        
        # Set a TTL (Time-To-Live) for the key to automatically expire the next day
        redis_client.expire(key, int(timedelta(days=1).total_seconds()))  # Convert to int here
        
        return current_requests

# Pydantic models
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: Optional[str]  # Make the name field optional
    age: Optional[int]
    address: Optional[Address]
rate_limiter=RateLimiter()
@app.get("/")
async def root():
    return {"message": "Welcome to the Updated Library Management System by Sunny Kumar!"}  
  
# Create student
@app.post("/students", response_model=Dict[str, str],dependencies=[Depends(rate_limiter.Rate_limiter)])
async def create_student(student: Student):
    student_dict = student.dict()
    result = student_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}

# List of students
@app.get("/students", response_model=List[Student], dependencies=[Depends(rate_limiter.Rate_limiter)])
async def list_students(country: str = Query(None), age: int = None):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = list(student_collection.find(query))
    return students

# Update student
@app.patch("/students/{id}", response_model=Dict[str, str], dependencies=[Depends(rate_limiter.Rate_limiter)])
async def update_student(id: str = Path(...), student_update: Dict[str, Any] = Body(...)):
    result = student_collection.update_one({"_id": ObjectId(id)}, {"$set": student_update})
    if result.modified_count == 1:
        return {"message": "Student updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")   

# Fetch student with id
@app.get("/students/{id}", response_model=Student, dependencies=[Depends(rate_limiter.Rate_limiter)])
async def fetch_student(id: str = Path(...)):
    student = student_collection.find_one({"_id": ObjectId(id)})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Delete student given id
@app.delete("/students/{id}", response_model=Dict[str, str], dependencies=[Depends(rate_limiter.Rate_limiter)])
async def delete_student(id: str = Path(...)):
    result = student_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Student deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

