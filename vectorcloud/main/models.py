from vectorcloud import db


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    path = db.Column(db.String())
    external_path = db.Column(db.String())
    cache = db.Column(db.String())
    folder = db.Column(db.String())


class PluginStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plugin = db.Column(db.String())
    entry_type = db.Column(db.String())
    value_json = db.Column(db.String())
    vector_id = db.Column(db.Integer)


class Vectors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String())
    cert_file = db.Column(db.String())
    ip = db.Column(db.String())
    name = db.Column(db.String())
    guid = db.Column(db.String())
    custom_name = db.Column(db.String())
    description = db.Column(db.String())


class Repositories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    name = db.Column(db.String())
    fp = db.Column(db.String())
    auto_update = db.Column(db.String())


db.create_all()
db.session.commit()
