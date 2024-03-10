from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import registry, Session

# Specify the path to your existing SQLite database file
database_file_path = 'mydb.db'

# Create an engine that connects to the SQLite database
engine = create_engine(f'sqlite:///{database_file_path}', echo=True)

# Initialize the registry
mapper_registry = registry()

# Initialize metadata object
metadata = MetaData()

# Reflect the existing tables
metadata.reflect(bind=engine)

# Define a mapped class
@mapper_registry.mapped
class User:
    __table__ = metadata.tables['users']
    # Define the rest of your columns here if you need to interact with them in Python
    # id = Column(Integer, primary_key=True)
    # name = Column(String)
    # email = Column(String)
    # etc.

# Create a session to interact with the database
with Session(engine) as session:
    # For example, to query all users from the users table:
    users = session.execute(select(User)).scalars().all()
    for user in users:
        print(user.name, user.email)