Database Models
===============
VectorCloud uses an SQLite database using the SQLAlchemy ORM for storing some information. This information can
be used/altered by your code in scripts and plugins. All of the database models can be
found below.

Example:
    Query the database

    .. code-block:: python

       from vectorcloud.main.models import Vectors, Logbook

       vector = Vectors.query.filter_by(id=1).first()
       logbook_items = Logbook.query.all()

       print(vector.name)
       for item in logbook_items:
           print(item.name)

    Modify a row

    .. code-block:: python

       from vectorcloud.main.models import Vectors
       from vectorcloud import db

       vector = Vectors.query.filter_by(id=1).first()
       vector.custom_name = "Bob"
       db.session.merge(vector)
       db.session.commit()

    Create a row

    .. code-block:: python

       from datetime import datetime
       from vectorcloud.main.models import Logbook
       from vectorcloud import db

       logbook_item = Logbook()
       logbook_item.name = "Something happened"
       logbook_item.info = "Err info not found"
       logbook_item.log_type = "fail"
       logbook_item.dt = datetime.now()
       db.session.add(logbook_item)
       db.session.commit()

    Delete a row

    .. code-block:: python

       from vectorcloud.main.models import Logbook
       from vectorcloud import db

       Logbook.query.filter_by(id=1).delete()
       db.session.commit()

main.models:
------------
    .. automodule:: vectorcloud.main.models
        :members:

user_system.models:
-------------------
    .. automodule:: vectorcloud.user_system.models
        :members:
        :undoc-members: