import streamlit as st
import requests

# Define API base URL
API_BASE_URL = "http://127.0.0.1:8000"

# Function to fetch all todos
def fetch_todos():
    response = requests.get(f"{API_BASE_URL}/todos/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching todos")

# Function to create a todo
def create_todo(content):
    payload = {"content": content}
    response = requests.post(f"{API_BASE_URL}/todos/", json=payload)
    if response.status_code == 200:
        st.success("Todo created successfully")
    else:
        st.error("Error creating todo")

# Function to delete a todo
def delete_todo(todo_id):
    response = requests.delete(f"{API_BASE_URL}/todos/{todo_id}/")
    if response.status_code == 200:
        st.success("Todo deleted successfully")
    else:
        st.error("Error deleting todo")

# Function to update a todo
def update_todo(todo_id, content):
    payload = {"content": content}
    response = requests.put(f"{API_BASE_URL}/todos/{todo_id}/", json=payload)
    if response.status_code == 200:
        st.success("Todo updated successfully")
    else:
        st.error("Error updating todo")

# Streamlit UI
def main():
    st.title("Todo App")

    # Create Todo
    st.header("Create Todo")
    new_todo_content = st.text_input("Enter Todo Content")
    if st.button("Create"):
        if new_todo_content:
            create_todo(new_todo_content)
        else:
            st.warning("Todo content cannot be empty")

    # List Todos
    st.header("Todos")
    todos = fetch_todos()
    if todos:
        for todo in todos:
            todo_content = todo['content']
            todo_id = todo['id']
            st.write(f"- {todo_content}")
            if st.button(f"Delete {todo_id}"):
                delete_todo(todo_id)

    # Update Todo
    st.header("Update Todo")
    todo_id = st.text_input("Enter Todo ID to Update")
    updated_content = st.text_input("Enter Updated Content")
    if st.button("Update"):
        if todo_id and updated_content:
            update_todo(int(todo_id), updated_content)
        else:
            st.warning("Todo ID and Updated Content cannot be empty")

if __name__ == "__main__":
    main()