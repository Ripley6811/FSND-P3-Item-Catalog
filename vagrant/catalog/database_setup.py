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


def get_database_session(db_echo=False):
    """Returns a session for executing queries.
    
    Connects to a database, creates an engine and returns a session connection
    to the engine.
    
    Args:
        db_echo: Boolean passed to create_engine's echo arg.
        
    Returns:
        A SQLAlchemy Session instance.
    """
    if use_postgresql:
        engine = create_engine(postgres_dbapi + database_name, echo=db_echo)
        print('Connected to PostgreSQL: ' + database_name)
    else:
        engine = create_engine(sqlite_dbapi + database_name, echo=db_echo)
        print('Connected to SQLite: ' + database_name)
    return sessionmaker(bind=engine)()


sqlite_dbapi = 'sqlite:///'
postgres_dbapi = 'postgresql+psycopg2:///'
database_name = 'resttest'

# Set this to "True" to use postgresql db or "False" for sqlite local file.
use_postgresql = True # Boolean


if __name__ == '__main__':
    """Sets up a new database with the tables defined above.
    
    Deletes the database if it already exists and creates a new database in
    its place. The tables are defined in file as classes that inherit a
    declarative_base() instance.
    """
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
        