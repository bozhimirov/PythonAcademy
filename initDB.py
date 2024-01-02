from sqlalchemy import create_engine

from model import Base


class CreateDB:
    """
        An engine class that makes a database for the app
    """
    def __init__(self) -> None:
        """
            constructor that initialize app engine and creates the DB for the app
        """
        engine = create_engine('sqlite:///mydatabase.db')
        Base.metadata.create_all(engine)
