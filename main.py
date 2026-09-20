import streamlit as st
import funqctions

todos = funqctions.get_todos()


st.title('My TODO APP')
st.subheader('This is my tasks')


for index, todo in enumerate(todos):
    stripped_todo = todo.strip()
    checkbox = st.checkbox(stripped_todo)
    if checkbox:
        todos.pop(index)
        funqctions.write_todos(todos)
        st.rerun()

with st.form('add_todo_form', clear_on_submit = True):
    new_todo = st.text_input("add new todo")
    submitted = st.form_submit_button('Add')
    if submitted:
        todo = new_todo.strip()
        if todo and (todo + "\n") not in todos:
            todos.append(todo + "\n") 
            funqctions.write_todos(todos)
            st.rerun()
