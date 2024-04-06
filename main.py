from typing import Dict, List
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Path, Query, Body
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Connect to MongoDB remotely
client = MongoClient("mongodb+srv://sunnykumar:sunny450@cluster0.nggkwbc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Cosmocloud"]
student_collection = db["student"]   

# Define student model
class Student(BaseModel):
    name: str
    age: int
    address: Dict[str, str]
#just to see     
@app.get("/")
async def root():
    return {"message": "Welcome to the Library Management System by Sunny Kumar!"}  
  

# Create student 
@app.post("/students", response_model=Dict[str, str])
async def create_student(student: Student):
    student_dict = student.dict()
    result = student_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}



# List  of students
@app.get("/students", response_model=List[Student])
async def list_students(country: str = Query(None), age: int = Query(None)):
    query = {}
    query = {}

    if country:
        query["address.country"] = country


    if age:
        query["age"] = {"$gte": age}

    students = list(student_collection.find(query))

    return students



# Fetch student with id
@app.get("/students/{id}", response_model=Student)
async def fetch_student(id: str = Path(...)):
    student = student_collection.find_one({"_id": ObjectId(id)})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")
    



# Update student given id
@app.patch("/students/{id}", response_model=Dict[str, str])
async def update_student(id: str = Path(...), student: Student = Body(None)):
    student_dict = student.dict()
    result = student_collection.update_one({"_id": ObjectId(id)}, {"$set": student_dict})
    if result.modified_count == 1:
        return {"message": "Student updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")
    




# Delete student given id
@app.delete("/students/{id}", response_model=Dict[str, str])
async def delete_student(id: str = Path(...)):
    result = student_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Student deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")



# doc_dummy=[

#     {
#         "name": "ansh",
#         "age": 22,
#         "address": {"city": "London", "country": "UK"}
#     },
#     {
#         "name": "manjeet",
#         "age": 25,
#         "address": {"city": "Paris", "country": "France"}
#     },
#     {
#         "name": "Emily",
#         "age": 21,
#         "address": {"city": "Berlin", "country": "Germany"}
#     },
#     {
#         "name": "saurabh",
#         "age": 23,
#         "address": {"city": "Tokyo", "country": "Japan"}
#     }
# ]
# ##just to see whether database updated or not
# for json in doc_dummy:
#     student_collection.insert_one(json)


#to run fastapipip 
# uvicorn main:app --reload

