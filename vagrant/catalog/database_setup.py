import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }

    



def get_database_session(db_echo=False):
    if use_postgresql:
        engine = create_engine(postgres_dbapi + database_name, echo=db_echo)
        print('Connected to PostgreSQL: ' + database_name)
    else:
        engine = create_engine(postgres_dbapi + database_name, echo=db_echo)
        print('Connected to SQLite: ' + database_name)
    return sessionmaker(bind=engine)()


use_postgresql = True
sqlite_dbapi = 'sqlite:///'
postgres_dbapi = 'postgresql+psycopg2:///'
database_name = 'resttest'


if __name__ == '__main__':
    '''Sets up a new database with the tables defined above.
    
    Deletes the database if it already exists and creates a new database in
    it's place. The tables are defined in file as classes that inherit the
    declarative_base().
    '''
    if use_postgresql:
        # Connect to default database: "postgres"
        engine = create_engine(postgres_dbapi + 'postgres', echo=True)
        conn = engine.connect()
        conn.execute('COMMIT') # "DROP DATABASE" cannot run inside transaction.
        conn.execute('DROP DATABASE IF EXISTS ' + database_name)
        conn.execute('COMMIT')
        conn.execute('CREATE DATABASE ' + database_name)
        conn.close()
        
        engine = create_engine(postgres_dbapi + database_name, echo=True)
        Base.metadata.create_all(engine)
        
    else: # Connect to sqlite local database.
        try:
            os.remove(database_name)
        except OSError:
            pass
        engine = create_engine(sqlite_dbapi + database_name, echo=True)
        Base.metadata.create_all(engine)
        