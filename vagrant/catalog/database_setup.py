#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from sqlalchemy import Column as Col, ForeignKey
from sqlalchemy import UniqueConstraint, CheckConstraint
from sqlalchemy import Integer, Unicode as Uni
from sqlalchemy import CheckConstraint as Check
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


###############################################################################
# Tables
###############################################################################
class Restaurant(Base):
    """Restaurant table in the database.

    Columns:
        ========== ======= =====
        name       type    description
        ========== ======= =====
        id         integer Primary key
        name       unicode Name of restaurant
        phone      unicode Phone number
        note       unicode Information about restaurant
        created_by integer Foreign key for a user record
        ========== ======= =====

    Relationships:
        ========= ======== ==========
        name      table    type
        ========= ======== ==========
        menu_item MenuItem One-to-Many
        ========= ======== ==========
    """
    __tablename__ = 'restaurant'

    id = Col(Integer, primary_key=True)  # Auto-serialized by SQLAlchemy
    name = Col(Uni(250), nullable=False)
    phone = Col(Uni(50), default=u'')
    note = Col(Uni(250), default=u'')
    created_by = Col(Integer, ForeignKey('user.id'), nullable=False)

    menu_items = relationship('MenuItem', cascade='delete')

    @property
    def sdict(self):
        """Return object data in serializeable format"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MenuItemRating(Base):
    """Menu item rating table in the database.

    Columns:
        ======= ======= ==============
        name    type    description
        ======= ======= ==============
        id      integer Primary key
        rating  integer Rating of 0 to 3
        item_id integer Foreign key for a menu item record
        user_id integer Foreign key for a user record
        ======= ======= ==============

    Relationships:
        ========= ======== ==========
        name      table    type
        ========= ======== ==========
        item      MenuItem One-to-One
        ========= ======== ==========
    """
    __tablename__ = 'menu_item_rating'

    id = Col(Integer, primary_key=True)
    user_id = Col(Integer, ForeignKey('user.id'), nullable=False)
    item_id = Col(Integer, ForeignKey('menu_item.id'), nullable=False)
    rating = Col(Integer, Check('rating<4'), nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'item_id'),)

    item = relationship('MenuItem')

    @property
    def sdict(self):
        """Return object data in serializeable format"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MenuItem(Base):
    """Menu item table in the database.

    Columns:
        ============= ======= ==============
        name          type    description
        ============= ======= ==============
        id            integer Primary key
        name          unicode Name of item
        description   unicode Description of food item
        price         unicode Price of food item
        course        unicode Type of food like main dish or dessert
        restaurant_id integer Foreign key for a restaurant record
        created_by    integer Foreign key for a user record
        ============= ======= ==============

    Relationships:
        ========== =============== ==========
        name       table           type
        ========== =============== ==========
        restaurant Restaurant      Many-to-One
        ratings    MenuItemRatings One-to-Many
        ========== =============== ==========
    """
    __tablename__ = 'menu_item'

    id = Col(Integer, primary_key=True)
    name = Col(Uni(80), nullable=False)
    description = Col(Uni(500), default=u'')
    price = Col(Uni(8), default=u'')
    course = Col(Uni(250), default=u'')
    restaurant_id = Col(Integer, ForeignKey('restaurant.id'), nullable=False)
    created_by = Col(Integer, ForeignKey('user.id'), nullable=False)

    restaurant = relationship('Restaurant')
    ratings = relationship('MenuItemRating', cascade='delete')

    @property
    def sdict(self):
        """Return object data in serializeable format.

        Also includes the restaurant name and totals for each rating:
            * restaurant_name - string
            * favorite_count - integer
            * good_count - integer
            * bad_count - integer
        """
        sd = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        sd['restaurant_name'] = self.restaurant.name
        sd['favorite_count'] = len([x for x in self.ratings if x.rating == 1])
        sd['good_count'] = len([x for x in self.ratings if x.rating == 2])
        sd['bad_count'] = len([x for x in self.ratings if x.rating == 3])
        return sd


class User(Base):
    """User table in the database.

    Columns:
        ======= ======= =====
        name    type    description
        ======= ======= =====
        id      integer Primary key
        name    unicode User name
        email   unicode User email
        picture unicode URI to user avatar
        ======= ======= =====

    Relationships:
        ================= =============== ==========
        name              table           type
        ================= =============== ==========
        menu_item_ratings MenuItemRatings One-to-Many
        ================= =============== ==========
    """
    __tablename__ = 'user'

    id = Col(Integer, primary_key=True)  # Auto-serialized by SQLAlchemy
    name = Col(Uni(250), nullable=False)
    email = Col(Uni(250), default=u'')
    picture = Col(Uni(250), default=u'')

    menu_item_ratings = relationship('MenuItemRating', cascade='delete')

    @property
    def sdict(self):
        """Return object data in serializeable format."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


###############################################################################
# Functions
###############################################################################
# Global variables for database API and database names.
sqlite_dbapi = 'sqlite:///'
postgres_dbapi = 'postgresql+psycopg2:///'
database_name = 'restaurants'  # Production database
test_database = 'rest_test'  # Testing database used by catalog_app_test.py.

# Set this to "True" to use postgresql db or "False" for sqlite local file.
use_postgresql = True  # Boolean


def get_database_session(echo=False, test=False):
    """Returns a session for executing queries.

    Connects to a database, creates an engine and returns a session connection
    to the engine.

    :arg boolean echo: Boolean passed to ``create_engine``'s echo arg.
    :arg boolean test: Boolean to use test db instead of the production db.

    :returns: A SQLAlchemy Session instance.
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


def create_all(echo=False, test=False):
    """Adds tables defined above to the database.

    Deletes the database if it already exists and creates a new database in
    its place. The tables are defined in file as classes that inherit a
    ``declarative_base()`` instance.

    :arg boolean echo: Boolean passed to ``create_engine``'s echo arg.
    :arg boolean test: Boolean to use test db instead of the production db.
    """
    db_name = database_name if not test else test_database
    if use_postgresql:
        # Connect to default database: "postgres"
        engine = create_engine(postgres_dbapi + db_name, echo=echo)
        Base.metadata.create_all(engine)

    else:
        # Connect to sqlite local database.
        engine = create_engine(sqlite_dbapi + db_name, echo=echo)
        Base.metadata.create_all(engine)


def drop_all(echo=False, test=True):
    """Deletes all tables from database.

    The ``test`` keyword is set to *True* by default because it is used mostly
    for testing and will help avoid accidentally dropping production tables.

    :arg boolean echo: Boolean passed to ``create_engine``'s echo arg.
    :arg boolean test: Boolean to use test db instead of the production db.
    """
    db_name = database_name if not test else test_database
    if use_postgresql:
        # Connect to default database: "postgres"
        engine = create_engine(postgres_dbapi + db_name, echo=echo)
        Base.metadata.drop_all(engine)

    else:
        # Connect to sqlite local database.
        engine = create_engine(sqlite_dbapi + db_name, echo=echo)
        Base.metadata.drop_all(engine)


def create_database(echo=False, test=False):
    """Creates a new empty database.

    Deletes the database if it already exists and creates a new database in
    its place.

    :arg boolean echo: Boolean passed to ``create_engine``'s echo arg.
    :arg boolean test: Boolean to use test db instead of the production db.
    """
    db_name = database_name if not test else test_database
    if use_postgresql:
        # Connect to default database: "postgres"
        engine = create_engine(postgres_dbapi + 'postgres', echo=echo)
        conn = engine.connect()
        conn.execute('COMMIT')  # "DROP DATABASE" can't run inside transaction.
        conn.execute('DROP DATABASE IF EXISTS ' + db_name)
        conn.execute('COMMIT')
        conn.execute('CREATE DATABASE ' + db_name)
        conn.close()
    else:
        # Connect to sqlite local database.
        try:
            os.remove(db_name)
        except OSError:
            pass
        engine = create_engine(sqlite_dbapi + db_name, echo=echo)


if __name__ == '__main__':
    create_database(echo=True)
    create_all(echo=True)
