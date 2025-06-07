from fastapi import FastAPI
import json 
app = FastAPI()

def load_data():
  with open('patients.json' , 'r') as f:
    data = json.load(f)
  return data

@app.get('/')
def read_root():
  return {'msg':'hello abhinay bir finish fastAPI'}

@app.get("/about")
def abt():
  return {'msg':'thisis abt page '}
  
@app.get("/view")
def view():
  data = load_data()
  return data




