from application import db
from application.models import records
from messaging import MessageHandler, MessageConsumer
import datetime
from multiprocessing.pool import Pool
import urllib2
from multiprocessing.dummy import Pool as ThreadPool
from sqlalchemy.sql import text
import json
from functools import partial

db_connection = db.engine.connect()

def read_message(recordid):
    db.engine.dispose()
    result = db.engine.execute(text("select record from records where id = :recid"), recid = recordid)
    msg_handler = MessageHandler()

    for row in result:
        msg_handler.add_message(row[0], "output_queue")

def read_multi_message(id_list):
    db.engine.dispose()
    result = db.engine.execute(text("select record from records where id = ANY(:recids)"), recids = id_list)
    msg_handler = MessageHandler()

    for row in result:
        msg_handler.add_message(row[0], "output_queue")

def read_id_from_queue():
    consumer = MessageConsumer("input_queue")
    consumer.listen()

def add_ids_to_queue(record_ids):
    msg_handler = MessageHandler()
    msg_handler.add_message(json.dumps({"ids":record_ids}), "input_queue")

def add_batch_ids_to_queue(record_ids, batch_size):
    batches = []
    for idx, cur_id in enumerate(record_ids):
        if idx % batch_size == 0:
            if idx == 0:
                some_ids = []
            else:
                batches.append(some_ids)
                some_ids = []
        some_ids.append(cur_id)

    msg_handler = MessageHandler()
    for batch in batches:
        msg_handler.add_message(json.dumps({"ids":batch}), "input_queue")

def add_batch_message(batch_ids):
    add_message({"ids" : records}, "input_queue")

class DBReader:

    def simple_read(self):
        start_time = datetime.datetime.now()
        sql = "select id, record from records"
        result = db_connection.execute(sql)

        msg_handler = MessageHandler()

        for row in result:
            msg_handler.add_message(row[1], "output_queue")

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        return time_taken

    def multi_proc(self):
        start_time = datetime.datetime.now()

        sql = "select id from records"
        result = db_connection.execute(sql)

        record_ids = [row[0] for row in result]

        p = Pool(4)
        p.map(read_message, record_ids)
        p.close()
        p.join()

        #for recid in record_ids:
        #    read_message(recid)

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        return time_taken

    def multi_proc2(self, batch):
        start_time = datetime.datetime.now()

        sql = "select id from records"
        result = db_connection.execute(sql)

        record_ids = []
        for idx, row in enumerate(result):
            if idx % int(batch) == 0:
                if idx == 0:
                    some_records = []
                else:
                    record_ids.append(some_records)
                    some_records = []
            some_records.append(row[0])


        p = Pool(4)
        p.map(read_multi_message, record_ids)

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        return time_taken

    def multi_proc3(self, batch):
        start_time = datetime.datetime.now()

        sql = "select count(id) from records"
        count_result = db_connection.execute(sql)

        for row in count_result:
            count = row[0]
            break

        sql = "select id from records"
        result = db_connection.execute(sql)

        record_ids = []
        for idx, row in enumerate(result):
            if (idx % int(batch) == 0) or (idx == count - 1):
                if idx == 0:
                    some_records = []
                else:
                    record_ids.append(some_records)
                    some_records = []
            some_records.append(row[0])


        #Add id messages to input queue
        msg_handler = MessageHandler()
        for records in record_ids:
            msg_handler.add_message(json.dumps({"ids":records}), "input_queue")

        worker_results = []
        p = Pool(4)
        for i in range(4):
            worker_results.append(p.apply_async(read_id_from_queue, ()))

        p.close()

        for r in worker_results:
            r.get()

        p.join() # This blocks until all the processes have finished

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        return time_taken

    def multi_proc4(self, batch):
        start_time = datetime.datetime.now()

        sql = "select count(id) from records"
        count_result = db_connection.execute(sql)

        for row in count_result:
            count = row[0]
            break

        sql = "select id from records"
        result = db_connection.execute(sql)

        record_ids = []
        for idx, row in enumerate(result):
            if (idx % int(batch) == 0) or (idx == count - 1):
                if idx == 0:
                    some_records = []
                else:
                    record_ids.append(some_records)
                    some_records = []
            some_records.append(row[0])

        p = Pool(4)
        #Add id messages to input queue
        p.map(add_ids_to_queue, record_ids)

        #Read ids from input_queue, read message from DB and write it to output_queue
        worker_results = []
        p = Pool(4)
        for i in range(4):
            worker_results.append(p.apply_async(read_id_from_queue, ()))

        p.close()

        for r in worker_results:
            r.get()

        p.join() # This blocks until all the processes have finished

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        return time_taken

    def multi_proc5(self, batch):
        start_time = datetime.datetime.now()

        sql = "select count(id) from records"
        count_result = db_connection.execute(sql)

        for row in count_result:
            count = row[0]
            break

        sql = "select id from records"
        result = db_connection.execute(sql)

        record_ids = []
        for idx, row in enumerate(result):
            if (idx % int(count/4) == 0) or (idx == count - 1): #4 because that is how many workers we have
                if idx == 0:
                    some_records = []
                else:
                    record_ids.append(some_records)
                    some_records = []
            some_records.append(row[0])

        input_pool = Pool(4)
        #Add id messages to input queue
        input_pool.map(partial(add_batch_ids_to_queue, batch_size=int(batch)), record_ids)
        input_pool.close()
        input_pool.join()


        output_pool = Pool(4)
        #Read ids from input_queue, read message from DB and write it to output_queue
        worker_results = []
        for i in range(4):
            worker_results.append(output_pool.apply_async(read_id_from_queue, ()))

        output_pool.close()

        for r in worker_results:
            r.get() # This reports results, including errors, of workers

        output_pool.join() # This blocks until all the processes have finished

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        return time_taken

    def multi_thread(self):

        start_time = datetime.datetime.now()

        sql = "select id from records"
        result = db_connection.execute(sql)

        record_ids = [row[0] for row in result]
        # Make the Pool of workers
        pool = ThreadPool(4)
        pool.map(read_message, record_ids)
        #close the pool and wait for the work to finish
        pool.close()
        pool.join()

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        return time_taken
