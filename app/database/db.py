from dotenv import load_dotenv
from models.base.base import Base
from os import getenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from local .env
load_dotenv()

# Get the specified .env variables
DB_DIALECT: str = getenv("DB_DIALECT")
DB_DATABASE: str = getenv("DB_DATABASE")
CREATE_MODELS: bool = getenv("CREATE_MODELS") == "True"
DEBUG: bool = getenv("DEBUG") == "True"

# Compose the DB URL (the connection string)
DB_URL: str = f"{DB_DIALECT}:///{DB_DATABASE}"

# Create the engine (and the database if it doesn't exist)
db_engine: Engine = create_engine(url=DB_URL, echo=DEBUG)

# Create a session maker
# Everytime the SessionLocal is instatiated,
# it will expose all the properties and methods of a Session
SessionLocal = sessionmaker(bind=db_engine)

# Create all the tables in the db
# This action should be executed just one time, but since the tables are
# already existing, from the second time the module is accessed,
# the tables won't be created again thanks to the parameter "checkfirst"

if CREATE_MODELS:
    Base.metadata.create_all(bind=db_engine)