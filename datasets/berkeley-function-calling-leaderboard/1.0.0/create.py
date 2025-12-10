import json
import os
import shutil

import audeer
import audformat


build_dir = audeer.mkdir("./build")
cache_dir = audeer.path("./cache")


def read_jsonl(file):
    with open(file) as fp:
        return [json.loads(line) for line in fp.readlines()]


db = audformat.Database(
    name="berkeley-function-calling-leaderboard",
    source="https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard",
    license="apache-2.0",
    license_url="https://www.apache.org/licenses/LICENSE-2.0",
    languages=["eng"],
    description=(
        "The Berkeley function calling leaderboard "
        "is a live leaderboard to evaluate the ability "
        "of different LLMs to call functions "
        "(also referred to as tools). "
        "We built this dataset from our learnings "
        "to be representative of most users' function calling use-cases, "
        "for example, "
        "in agents, as a part of enterprise workflows, etc. "
        "To this end, "
        "our evaluation dataset spans diverse categories, "
        "and across multiple languages. "
        ""
        "Checkout the Leaderboard at gorilla.cs.berkeley.edu/leaderboard.html "
        "and further info at "
        "https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard."
    ),
)

# Tables with question json files
db.schemes["topic"] = audformat.Scheme("str")
files = audeer.list_file_names(cache_dir, filetype="json", basenames=True)
for file in files:
    topic = audeer.basename_wo_ext(file).lower().replace("_", "-")
    audeer.mkdir(build_dir, "json", topic)
    question_file = audeer.path(cache_dir, file)
    answer_file = audeer.path(cache_dir, "possible_answer", file)
    questions = read_jsonl(question_file)
    if os.path.exists(answer_file):
        answers = read_jsonl(answer_file)
        answers_by_id = {answer["id"]: answer for answer in answers}
        for question in questions:
            answer = answers_by_id.get(question["id"])
            if answer is not None:
                question |= answer
    # Store one question (+ potential answer) per json file
    for n, question in enumerate(questions):
        path = audeer.path(build_dir, "json", topic, f"sample-{n}.json")
        with open(path, "w", encoding="utf-8") as fp:
            json.dump([question], fp, ensure_ascii=False, indent=2)
    index = audformat.filewise_index(
        [f"{topic}/sample-{n}.json" for n in range(len(questions))]
    )
    db[topic] = audformat.Table(index)
    db[topic]["topic"] = audformat.Column(scheme_id="topic")
    db[topic]["topic"].set(topic.removeprefix("bfcl-v3-"))

# Table with function definitions
doc_dir = "multi_turn_func_doc"
doc_files = audeer.list_file_names(
    audeer.path(cache_dir, doc_dir),
    basenames=True,
)
dst_files = [f"{file.replace('_', '-')}l" for file in doc_files]
table_id = doc_dir.replace("_", "-")
audeer.mkdir(build_dir, table_id)
index = audformat.filewise_index([f"{table_id}/{file}" for file in dst_files])
db[table_id] = audformat.Table(index)
for file, dst_file in zip(doc_files, dst_files):
    shutil.copyfile(
        audeer.path(cache_dir, doc_dir, file),
        audeer.path(build_dir, table_id, dst_file),
    )
db[table_id]["topic"] = audformat.Column(scheme_id="topic")
db[table_id]["topic"].set(audeer.basename_wo_ext(file) for file in dst_files)
db.save(build_dir)
