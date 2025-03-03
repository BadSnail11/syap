from pony.orm import *

settings = dict(
    sqlite = dict(provider = 'sqlite', filename = '.\data.db', create_db = True)
)

db = Database(**settings['sqlite'])


class Books(db.Entity):
    id = PrimaryKey(int, auto = True)
    name = Optional(str)
    description = Optional(str)
    size = Optional(int)

class Users(db.Entity):
    id = PrimaryKey(int, auto = True)
    login = Optional(str)
    password = Optional(str)


#### users


@db_session
def get_user(id: int) -> Users | None:
    try:
        return Users[id]
    except:
        return None

@db_session
def get_user_by_login(login: str) -> Users | None:
    try:
        return Users.get(login = login)
    except:
        return None

@db_session
def create_user(login: str, password: str) -> Users:
    try:
        return Users(login = login, password = password)
    except:
        pass


### books

@db_session
def get_book(id: int) -> Books | None:
    try:
        return Books[id]
    except:
        return None

@db_session
def get_all_books() -> list[Books] | None:
    try:
        return list(select(o for o in Books))
    except:
        return None

@db_session
def create_book(name: str, size: int, description: str = "") -> Books | None:
    try:
        return Books(name = name, description = description, size = size)
    except:
        return None

@db_session
def edit_book(id: int, name: str, size: int, description: str) -> Books | None:
    try:
        book = Books[id]
        book.name = name
        book.description = description
        book.size = size
        commit()
        return book
    except:
        return None
    
@db_session
def delete_book(id: int) -> None:
    try:
        Books[id].delete()
        commit()
    except:
        pass

db.generate_mapping()