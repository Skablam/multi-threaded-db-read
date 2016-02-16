import datetime
from sqlalchemy import Column, Integer, String
from application import db


class records(db.Model):

    id = Column(Integer, primary_key=True)
    record = db.Column(String)
    
    def __init__(self, record):
        self.record = record

    def __repr__(self):
        return self.record
