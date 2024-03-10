####################### Imports #######################

from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import hashlib
import json

####################### Base Setup #######################

DATABASE_URL = "sqlite:////app/db/thread.db" # local filename
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

class ChatThread(Base):
    __tablename__ = 'User Chat Thread History' # rename this to User's Thread History

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    name = Column(String)
    model = Column(String)
    history = Column(JSON)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

####################### General Utility Functions #######################

def generate_hash():
    chatThread_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hash = hashlib.sha256(chatThread_time.encode()).hexdigest()
    return hash

def count_rows():
    return session.query(ChatThread).count()

def emptyDB():
    Base.metadata.drop_all(engine, tables=[ChatThread.__table__])

####################### ChatThread Specific Utility Functions  #######################

def create_chatThread():
    default_chat_name = "New chat"
    default_model = "gpt-3.5-turbo"
    chatThread_time = datetime.now()
    new_ChatThread = ChatThread(
                                id=count_rows() + 1,
                                created=chatThread_time, 
                                name=default_chat_name,
                                model=default_model,
                                history=json.dumps([]))
    session.add(new_ChatThread)
    session.commit()

def appendto_chatThread(chatThread_id, content):
    chatThread = session.query(ChatThread).filter(ChatThread.id == chatThread_id).first()

    if chatThread:
        existing_content = chatThread.history
        
        if isinstance(existing_content, str):
            try:
                print(f"\n\n################\n\nExisting Content:\n{existing_content}\n################\n\n")
                existing_json = json.loads(existing_content)
            except json.JSONDecodeError:
                existing_json = []
        else:
            existing_json = []

        print(f"\n\n################\n\nDeserialized Content:\n{existing_json}\n################\n\n")
        
        new_data = json.loads(content)
        print(f"\n\n################\n\nNew Data:\n{new_data}\n################\n\n")
        
        existing_json.append(new_data)
        print(f"\n\n################\n\nExisting JSON:\n{existing_json}\n################\n\n")
        
        chatThread.history = json.dumps(existing_json)
        
        session.commit()
        print(f"Thread with ID {chatThread_id} updated content successfully")
    else:
        print(f"No thread found with ID {chatThread_id}. Nothing appended.")


def delete_chatThread(chatThread_id):
    thread = session.query(ChatThread).filter(ChatThread.id == chatThread_id).first()
    if thread:
        session.delete(thread)
        session.commit()
        print(f"Thread with ID {chatThread_id} deleted successfully.")
    else:
        print(f"No thread found with ID {chatThread_id}. Nothing deleted.")

def edit_chatThread_name(chatThread_id, new_name):
    chatThread = session.query(ChatThread).filter(ChatThread.id == chatThread_id).first()
    if chatThread:
        chatThread.name = new_name
        session.commit()
        print(f"ChatThread with ID {chatThread_id} name updated to '{new_name}'")
    else:
        print(f"No ChatThread found with ID {chatThread_id}")

def generate_chatThread_name():
    return "New chat"

####################### DB Test Blocks  #######################

# create_chatThread()
# appendto_chatThread(1, json.dumps({"test":"huh"},indent=4))
# delete_chatThread(2)
# Base.metadata.drop_all(engine)
# emptyDB()