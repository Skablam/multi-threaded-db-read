# multi-threaded-db-read

### Idea behind this repo

I wanted to explore how I could multi-thread or multi-process reading from a database
and writing to a RabbitMQ queue in the fastest possible method using Python.

### Getting started

```
vagrant up
sudo pip install -r requirements.txt
python manage.py db upgrade
source run.sh
```

### Add data

By default the populatedb.py script adds 10000 25kb rows to a postgres table
called records in a database also called records.

```
python populatedb.py
```

You can access the database with the following command

```
psql records
```

### Hitting the service

Currently, I have tried out several different methods for reading from a database. The end points are:

```
/simpleread
/multiproc
/multiproc/<batch>
/multiproc2/<batch>
/multiproc3/<batch>
/multiproc4/<batch>
/multiproc5/<batch>
/multithread
```

You can hit any one of them using curl e.g.

```
curl localhost:5000/simpleread

or

curl localhost:5000/multiproc/1000
```

The batch parameter indicates how many message ids will be included in any message.
