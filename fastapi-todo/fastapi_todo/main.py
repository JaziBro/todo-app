#main.py
from typing import Annotated
from sqlmodel import  Session, select
from fastapi import FastAPI, Depends, HTTPException
from fastapi_todo.database import database
from fastapi_todo.models import models



app = FastAPI(
    lifespan=database.lifespan, title="Todo API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000/", 
            "description": "Development Server"
        }
    ] 
)

database.create_db_and_tables()


@app.get('/')
def read_root():
    return {"Hello": "World"}

# add todo
@app.post("/todos/", response_model=models.Todo)
def create_todo(todo: models.Todo, session: Annotated[Session, Depends(database.get_session)]):
    if todo.content:
        session.add(todo)
        session.commit()
        session.refresh(todo) 
        return todo
    else:
        raise HTTPException(status_code=400, detail= "Content cannot be empty")

# read todos
@app.get("/todos/", response_model=list[models.Todo])
def read_todos(session: Annotated[Session, Depends(database.get_session)]):
        todos = session.exec(select(models.Todo)).all()
        return todos

@app.get("/todos/{todo_id}/", response_model=models.Todo)
def read_todo(todo_id: int, session: Session = Depends(database.get_session)):
    todo = session.get(models.Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")
    return todo

# delete todo
@app.delete("/todos/{todo_id}/")
def delete_todo(todo_id: int, session: Annotated[Session, Depends(database.get_session)]):
    todo = session.get(models.Todo, todo_id)

    if todo:
        session.delete(todo)
        session.commit()
        return {"message": f"Todo with ID {todo_id} deleted successfully"}   
    else:
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")

# update a todo
@app.put("/todos/{todo_id}/", response_model=models.Todo)  
def update_todo(todo_id: int, todo_update: models.TodoUpdate, session: Annotated[Session, Depends(database.get_session)]):
        todo = session.get(models.Todo, todo_id)
        if todo:
            if todo_update.content: 
                todo.content = todo_update.content
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return todo  
        else:
            raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not dound")


