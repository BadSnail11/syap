from pony.orm import *
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

settings = dict(
    sqlite = dict(provider='sqlite', filename=os.getenv("DB_PATH"), create_db=True)
)

db = Database(**settings['sqlite'])

class Users(db.Entity):
    id = PrimaryKey(int, auto = True)
    telegram_id = Optional(str)

class Tasks(db.Entity):
    id = PrimaryKey(int, auto = True)
    text = Optional(str)
    priority = Optional(str)
    timestamp = Optional(float)

class User_To_Tasks(db.Entity):
    id = PrimaryKey(int, auto = True)
    user_id = Optional(int)
    task_id = Optional(int)

@db_session
def getUser(id: int) -> Users | None:
    try:
        return Users[id]
    except:
        return None
    
@db_session
def getUsers() -> list[Users] | None:
    try:
        return list(select(o for o in Users))
    except:
        return None

@db_session
def getUserByTelegram(telegram_id: str) -> Users | None:
    try:
        user = Users.get(telegram_id=telegram_id)
        return user
    except:
        return None

@db_session
def getUserByTask(task: Tasks) -> Users | None:
    try:
        link = User_To_Tasks.get(task_id=task.id)
        return Users[link.user.id]
    except:
        return None
    
@db_session
def addUser(telegram_id: int) -> Users | None:
    try:
        user = Users()
        user.telegram_id = telegram_id
        commit()
        return user
    except:
        return None

@db_session
def getTask(id: int) -> Tasks | None:
    try:
        return Tasks[id]
    except:
        return None

@db_session
def getTasksByUser(user: Users) -> list[Tasks] | None:
    try:
        links = list(select(o for o in User_To_Tasks if o.user_id == user.id))
        tasks = []
        for link in links:
            for task in list(select(o for o in Tasks if o.id == link.task_id)):
                tasks.append(task)
        return tasks
    except:
        return None
    
@db_session
def addTask(text: str, priority: str, timestamp: float) -> Tasks | None:
    try:
        task = Tasks()
        task.text = text
        task.priority = priority
        task.timestamp = timestamp
        commit()
        return task
    except:
        return None
    
@db_session
def editTask(id: int, text: str, priority: str, timestamp: float) -> Tasks | None:
    try:
        task = Tasks[id]
        task.text = text if (text) else task.text
        task.priority = priority if (priority) else task.priority
        task.timestamp = timestamp if (timestamp) else task.timestamp
        commit()
        return task
    except:
        return None
    
@db_session
def deleteTask(id: int) -> None:
    try:
        task = Tasks[id]
        task.delete()
        commit()
    except:
        pass
    
@db_session
def addLink(task_id: int, user_id: int) -> User_To_Tasks | None:
    try:
        link = User_To_Tasks()
        link.task_id = task_id
        link.user_id = user_id
        commit()
        return link
    except:
        return None
    
class priorities:
    low="низкий"
    medium="средний"
    high="высокий"

db.generate_mapping()