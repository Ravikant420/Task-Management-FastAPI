from fastapi import FastAPI, status, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Annotated, Optional
import json
from pathlib import Path


app = FastAPI()

FILE_PATH = Path("tasks.json")
class TaskCreate(BaseModel):

    title: Annotated[str, Field(..., description='Title of the Task', examples=['Learn FastAPI'])]
    description: Annotated[str, Field(..., description='Description of the Task', examples=['Understand GET requests'])]
    completed: Annotated[bool, Field(..., description='Its completed or not', examples=[False])]


class TaskUpdate(BaseModel):
    title: Annotated[Optional[str], Field(default=None)]
    description: Annotated[Optional[str], Field(default=None)]
    completed: Annotated[Optional[bool], Field(default=None)]


def load_data():
    if not FILE_PATH.exists():
        return {}

    try:

        with open(FILE_PATH,"r") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid task data format")
        
        return data
    except json.JSONDecodeError:
        return {}


    

def save_data(data):
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f , indent=4)



def generate_task_id(data):
    if not data:
        return 1

    else:
        existingid = []
        for task_id in data.keys():
            existingid.append(int(task_id))
        return max(existingid) + 1

    



@app.get('/')
def root():
    return {'message': 'Welcome to task manager API'}

@app.get('/about')
def about():
    return {
        "project":"Task Manager",
        "version":"1.0",
        "developer": "Ravi Kant"
    }

@app.get('/health')
def health():
    return {'status':'healthy'}



@app.get('/tasks')
def all_tasks():
    data = load_data()
    return data

@app.get('/tasks/{task_id}')
def one_task(task_id: int):
    #load the data
    data = load_data()

    if str(task_id) not in data:
        raise HTTPException(status_code = 404, detail='Task not found')
    return {
        "id": task_id,
        **data[str(task_id)]
    }

@app.post('/tasks',status_code= status.HTTP_201_CREATED)
def create_tasks(task : TaskCreate):
    data = load_data()

    # generate unique id
    task_id = generate_task_id(data)

    # create the task record
    new_task = task.model_dump()


    #store it in json
    data[str(task_id)] = new_task
    save_data(data)

    return {
        "id" : task_id,
        **new_task
    }

    
@app.put('/tasks/{task_id}')
def update_task(task_id: int, task_update : TaskUpdate):
    # load the data
    data = load_data()

    if str(task_id) not in data:
        raise HTTPException(status_code=404, detail='Task not found')

    previous_data = data[str(task_id)]
    new_data = task_update.model_dump(exclude_unset=True)

    for key, value in new_data.items():
        previous_data[key] = value

    data[str(task_id)] = previous_data
    save_data(data)
    return data[str(task_id)]



@app.delete('/tasks/{task_id}')
def delete_task(task_id: int):
    # load data
    data = load_data()
    if str(task_id) not in data:
        raise HTTPException(status_code=404, detail='Task Not found')
    else:
        del data[str(task_id)]
        save_data(data)
    return {'message': f'Task {task_id} Deleted Successfully'}


@app.get('/complete')
def completed_tasks(complete: bool = Query(..., description = 'Get all completed tasks or pending tasks based on True or False')):

    require_data= []
    data = load_data()
    for task_id, task in data.items():
        if  task["completed"] == complete :
            require_data.append({
                'id': int(task_id),
                **task
            })

    return require_data