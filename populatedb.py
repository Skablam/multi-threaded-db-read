from __future__ import print_function
from application import db
from application.models import records
import sys

with open("samplerecord.txt") as f:
    rec = f.read()

for i in range(0, 10000):
    record = records(rec)
    try:
        db.session.add(record)
    except Exception as err:
        db.session.rollback()

print("")
print("Commit...")
db.session.commit()
