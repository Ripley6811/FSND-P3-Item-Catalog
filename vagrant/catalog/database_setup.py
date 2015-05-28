#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
#import sys
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True) # Auto-serialized by SQLAlchemy
    name = Column(Unicode(250), nullable=False)
    phone = Column(Unicode(50), default=u'')
    note = Column(Unicode(250), default=u'')
    
    menu_items = relationship('MenuItem', cascade='delete')

    @property
    def sdic(self):
        """Return object data in easily serializeable format"""
        return to_serializable_dic(self)


class MenuItem(Base):
    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(80), nullable=False)
    description = Column(Unicode(500))
    price = Column(Unicode(8))
    course = Column(Unicode(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), 
                           nullable=False)
    rating = Column(Integer, default=0)
    
    restaurant = relationship(Restaurant)

    @property
    def sdic(self):
        """Return object data in easily serializeable format"""
        d = to_serializable_dic(self)
        # Include restaurant name.
        d['restaurant_name'] = self.restaurant.name
        return d

    
def to_serializable_dic(obj):
    """Converts the object into a serializable dictionary.
    
    Args:
        obj: Reference to an object.
    
    Returns:
        A python dictionary.
    """
    filtered_copy = {}
    for key, value in obj.__dict__.iteritems():
        if not key.startswith(u'_'): # Skip private variables/references.
            filtered_copy.update({key:value})
    return filtered_copy


def get_database_session(echo=False, test=False):
    """Returns a session for executing queries.
    
    Connects to a database, creates an engine and returns a session connection
    to the engine.
    
    Args:
        echo: Boolean passed to create_engine's echo arg.
        test: Boolean to use test database instead of the production one.
        
    Returns:
        A SQLAlchemy Session instance.
    """
    db_name = database_name if not test else test_database
    if use_postgresql:
        engine = create_engine(postgres_dbapi + db_name, echo=echo)
        if echo: 
            print('Connected to PostgreSQL: ' + db_name)
    else:
        engine = create_engine(sqlite_dbapi + db_name, echo=echo)
        if echo:
            print('Connected to SQLite: ' + db_name)
    return sessionmaker(bind=engine)()


sqlite_dbapi = 'sqlite:///'
postgres_dbapi = 'postgresql+psycopg2:///'
database_name = 'restaurants'
test_database = 'rest_test'

# Set this to "True" to use postgresql db or "False" for sqlite local file.
use_postgresql = True # Boolean


def create_all(echo=False, test=False):
    """Adds tables defined above to the database.
    
    Deletes the database if it already exists and creates a new database in
    its place. The tables are defined in file as classes that inherit a
    declarative_base() instance.
    """
    db_name = database_name if not test else test_database
    if use_postgresql:
        # Connect to default database: "postgres"
        engine = create_engine(postgres_dbapi + db_name, echo=echo)
        Base.metadata.create_all(engine)
        
    else: # Connect to sqlite local database.
        engine = create_engine(sqlite_dbapi + db_name, echo=echo)
        Base.metadata.create_all(engine)
        
        
def drop_all(echo=False, test=False):
    """Deletes all tables from database."""
    db_name = database_name if not test else test_database
    if use_postgresql:
        # Connect to default database: "postgres"
        engine = create_engine(postgres_dbapi + db_name, echo=echo)
        Base.metadata.drop_all(engine)
        
    else: # Connect to sqlite local database.
        engine = create_engine(sqlite_dbapi + db_name, echo=echo)
        Base.metadata.drop_all(engine)
        

def create_database(echo=False, test=False):
    """Creates a new empty database.
    
    Deletes the database if it already exists and creates a new database in
    its place. 
    """
    db_name = database_name if not test else test_database
    if use_postgresql:
        # Connect to default database: "postgres"
        engine = create_engine(postgres_dbapi + 'postgres', echo=echo)
        conn = engine.connect()
        conn.execute('COMMIT') # "DROP DATABASE" cannot run inside transaction.
        conn.execute('DROP DATABASE IF EXISTS ' + db_name)
        conn.execute('COMMIT')
        conn.execute('CREATE DATABASE ' + db_name)
        conn.close()
    else: # Connect to sqlite local database.
        try:
            os.remove(db_name)
        except OSError:
            pass
        engine = create_engine(sqlite_dbapi + db_name, echo=echo)
    

if __name__ == '__main__':
    create_database(echo=True)
    create_all(echo=True)