from fastapi import FastAPI , Path, HTTPException,  Query
import json 
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
app = FastAPI()
from fastapi.responses import JSONResponse
class Patient(BaseModel):
  id: Annotated[str, Field(..., description="The unique identifier for the patient", example="P001")]   
  name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
  city: Annotated[str, Field(..., description="The city where the patient resides", example="New York")] 
  age: Annotated[int, Field(..., gt=0, description="The age of the patient", example=30)]
  gender: Annotated[Literal['M', 'F', 'Others'], Field(..., description="gender of the patient", example="M")]
  height: Annotated[float, Field(..., description="The height of the patient in mtrs", example=175.5)]
  weight: Annotated[float, Field(...,gt=0, description="The weight of the patient in kilograms", example=70.0)]
  @computed_field
  @property
  def bmi(self) -> float:
    """Calculate the Body Mass Index (BMI) of the patient."""
    return round(self.weight / (self.height ** 2), 2)
  @computed_field
  @property
  def verdict(self) -> str:
    """Predict the health status based on BMI."""
    if self.bmi < 18.5:
      return "Underweight"
    elif 18.5 <= self.bmi < 24.9:
      return "Normal weight"
    elif 25 <= self.bmi < 29.9:
      return "Overweight"
    else:
      return "Obesity"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['M', 'F', 'Others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = Patient(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})


def load_data():
  with open('patients.json' , 'r') as f:
    data = json.load(f)
  return data
def save_data(data):
  with open('patients.json', 'w') as f:
    json.dump(data, f, indent=4)
@app.get('/')
def read_root():
  return {'msg':'hello abhinay bir finish fastAPI'}

@app.get("/abt")
def abt():
  return {'msg':'thisis abt page '}
  
@app.get("/view")
def view():
  data = load_data()
  return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to view", example="12345")):
  data = load_data()
  if patient_id in data:
    return data[patient_id]
  # return {'error': 'patient not found'}
  raise HTTPException(status_code=404, detail='Patient not found')


@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="Sort patients by 'name' or 'age'", example="name"),
                  order: str = Query("asc", description="Order of sorting: 'asc' for ascending, 'desc' for descending", example="asc")
                  ):
  patient_data = load_data()
  valid_sort_fields = list(next(iter(patient_data.values())).keys())

  if sort_by not in valid_sort_fields:
    raise HTTPException(status_code=400, detail=f"Invalid sort parameter. Use {patient_data}.")
  
  if order not in ['asc', 'dsc']:
    raise HTTPException(status_code=400, detail="Invalid order parameter. Use 'asc' or 'dsc'.")
  reverse_order = order == 'dsc'
  sorted_data = sorted(patient_data.items(), key=lambda x: x[1][sort_by], reverse=reverse_order)
  return {k: v for k, v in sorted_data}


@app.post("/add")
def add_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists.")
    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient added successfully", "patient": patient.model_dump()})