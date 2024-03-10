from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLite URL using the in-memory database for simplicity
DATABASE_URL = "sqlite:///mydb.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Define a base class for declarative schema definition
Base = declarative_base()

# Define a User class which will be mapped to the "users" table
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

# Create the database table associated with the User class
Base.metadata.create_all(engine)

# Bind the engine to a Session class
Session = sessionmaker(bind=engine)

# Create a session instance to interact with the database
session = Session()

# Create a new user instance
users = [
    User(name='Joshua Jerome', email='joshua.jerome@gmail.com'),
]

# Add the new user to the session
for u in users:
    session.add(u)

# Commit the session to write changes to the database
session.commit()

# Query the database to find users with the name 'John Doe'
users = session.query(User).filter_by(name='Joshua Jerome').all()

# Print out the user(s) found
for user in users:
    print(f'User ID: {user.id}, Name: {user.name}, Email: {user.email}')

# Close the session
session.close()