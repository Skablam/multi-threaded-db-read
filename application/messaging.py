from kombu import Connection
import kombu
import kombu.connection
import kombu.entity
import kombu.messaging
import datetime
from application import db
from application.models import records
from sqlalchemy.sql import text
import json

class MessageHandler:

    def __init__(self):
        self.conn = Connection('amqp://guest:guest@localhost:5672//')

    def add_message(self, message, queue_name):

        simple_queue = self.conn.SimpleQueue(queue_name)
        simple_queue.put(message)
        simple_queue.close()

    def get_message(self, queue_name):
        simple_queue = self.conn.SimpleQueue(queue_name)
        message = simple_queue.get(block=True, timeout=1)
        message.ack()
        simple_queue.close()
        return message

class MessageConsumer:

    def __init__(self, queue_name):
        self.queue_name = queue_name
        params = {
            'hostname': 'localhost',
            'port': 5672,
            'virtual_host': '/',
        }

        self.connection = kombu.connection.BrokerConnection(**params)
        self.connection.connect()

        self.db_connection = db.engine.connect()

    def listen(self):
        self.exchange = kombu.entity.Exchange(name='test',
                                         type='fanout',
                                         durable=False,
                                         auto_delete=False)

        queue1 = kombu.Queue(name=self.queue_name, exchange=self.exchange, routing_key='input')
        queue1.maybe_bind(self.connection)
        queue1.declare()

        def process_message(body, message):
            #db.engine.dispose()
            id_list = json.loads(message.body)["ids"]
            result = self.db_connection.execute(text("select record from records where id = ANY(:recids)"), recids = id_list)

            for row in result:
                self.send(row[0], "output_queue")
            message.ack()

        self.consumer = kombu.Consumer(self.connection, queues=queue1, callbacks=[process_message], accept=[])
        self.consumer.consume()

        while True:
            try:
                self.connection.drain_events(timeout=1)
            except Exception as err:
                 break

    def send(self, message, queue_name):
        simple_queue = self.connection.SimpleQueue(queue_name)
        simple_queue.put(message)
        simple_queue.close()
