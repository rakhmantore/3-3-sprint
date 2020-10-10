from flask import Flask
import openaq
from flask_sqlalchemy import SQLAlchemy


APP = Flask(__name__)
api = openaq.OpenAQ()


APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '<Datetime %r>  <Value %r>' %(self.datetime, self.value)


@APP.route('/')
def root():
    """Base view."""
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    l = []
    dicts = body['results']
    for d in dicts:
        #(utc_datetime, value) = d.get('date').get('utc'), d.get('value')
        #l.append((utc_datetime, value))
        db_record = Record(datetime=d.get('date').get('utc'), value=d.get('value'))
        DB.session.add(db_record)
    DB.session.commit()
    l = Record.query.filter(Record.value >= 10).all()
    return str(l)




@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    DB.session.commit()
    return 'Data refreshed!'
