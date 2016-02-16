from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import os

app = Flask(__name__)

app.config.from_object("config.Config")
db = SQLAlchemy(app)
