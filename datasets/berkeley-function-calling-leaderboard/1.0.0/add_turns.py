import json

import audeer
import audformat


build_dir = audeer.path("./build")


def number_of_turns(json_file):
    with open(audeer.path(build_dir, json_file)) as fp:
        content = json.load(fp)
        return len(content)


db = audformat.Database.load(build_dir)
db.schemes["turns"] = audformat.Scheme("int")

for table in list(db):
    turns = [number_of_turns(file) for file in db[table].files]
    db[table]["turns"] = audformat.Column(scheme_id="turns")
    db[table]["turns"].set(turns)

db.save(build_dir)
