from application import app
from messaging import MessageHandler
from flask import request
from application.dbreader import DBReader

import json

@app.route("/health")
def check_status():
    return "Status OK"

@app.route("/message", methods=["GET","POST"])
def messages():
    if request.method == 'POST':
        message = request.data
        msg_handler = MessageHandler()

        msg_handler.add_message(message, "read_ids")
        return "Message added: {0}".format(message)
    else:
        msg_handler = MessageHandler()
        message = msg_handler.get_message("read_ids")
        return "Message retrieved: {0}".format(message)

@app.route("/simpleread")
def simple():
    reader = DBReader()
    time_taken = reader.simple_read()
    return "Simple read time taken: {0} seconds".format(time_taken)

@app.route("/multiproc")
def multi():
    reader = DBReader()
    time_taken = reader.multi_proc()
    return "Multi process time taken: {0} seconds".format(time_taken)

@app.route("/multiproc2/<batch>")
def multi2(batch):
    reader = DBReader()
    time_taken = reader.multi_proc2(batch)
    return "Multi process 2 time taken: {0} seconds".format(time_taken)

@app.route("/multiproc3/<batch>")
def multi3(batch):
    reader = DBReader()
    time_taken = reader.multi_proc3(batch)
    return "Multi process 3 time taken: {0} seconds".format(time_taken)

@app.route("/multiproc4/<batch>")
def multi4(batch):
    reader = DBReader()
    time_taken = reader.multi_proc4(batch)
    return "Multi process 4 time taken: {0} seconds".format(time_taken)

@app.route("/multiproc5/<batch>")
def multi5(batch):
    reader = DBReader()
    time_taken = reader.multi_proc5(batch)
    return "Multi process 5 time taken: {0} seconds".format(time_taken)

@app.route("/multithread")
def thread():
    reader = DBReader()
    time_taken = reader.multi_thread()
    return "Multi thread time taken: {0} seconds".format(time_taken)
