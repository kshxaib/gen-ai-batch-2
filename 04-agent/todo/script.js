const input = document.getElementById('todo-input');
const addBtn = document.getElementById('add-btn');
const todoList = document.getElementById('todo-list');

addBtn.addEventListener('click', addTask);
input.addEventListener('keypress', function(e) {
    if(e.key === 'Enter') addTask();
});

function addTask() {
    const task = input.value.trim();
    if(task === '') return;
    const li = document.createElement('li');
    li.textContent = task;

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.className = 'delete-btn';
    delBtn.onclick = function() {
        todoList.removeChild(li);
    }

    li.appendChild(delBtn);
    todoList.appendChild(li);
    input.value = '';
}