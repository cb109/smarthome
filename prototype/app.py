# pip install flask
# FLASK_APP=app.py flask run ---host=0.0.0.0 --port=8050

import json
import os
from datetime import datetime

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request


app = Flask(__name__)


db_file = "samples.json"


def save_to_db(sample):
    data = {"samples": []}
    if os.path.isfile(db_file):
        content = open(db_file).read()
        try:
            data = json.loads(content)
        except ValueError as err:
            print(err)

    sample["timestamp"] = datetime.now().isoformat()
    data["samples"].append(sample)

    with open(db_file, "w") as f:
        content = json.dumps(data, indent=4)
        f.write(content)

    print("Sample written: " + str(sample))


@app.route("/reboot", methods=["POST"])
def reboot():
    filepath = "reboot_" + datetime.now().isoformat()
    filepath = filepath.replace(":", "-")
    filepath = filepath.replace(".", "-")
    with open(filepath, "w") as f:
        f.write("")
    return jsonify(True)


@app.route("/sensor", methods=["GET", "POST"])
def sensor():
    if request.method == "GET":
        content = open(db_file).read()
        data = json.loads(content)
        return jsonify(data)

    elif request.method == "POST":
        sample = request.get_json(force=True)
        save_to_db(sample)
        return jsonify(sample)


@app.route("/graph", methods=["GET"])
def graph():
    content = open(db_file).read()
    data = json.loads(content)
    as_series = {
        "temperatures": [],
        "humidities": [],
        "timestamps": [],
    }
    for sample in data["samples"]:
        as_series["temperatures"].append(sample["temperature"])
        as_series["humidities"].append(sample["humidity"])
        as_series["timestamps"].append(sample["timestamp"])

    return render_template(
        "graph.html",
        temperatures=as_series["temperatures"],
        humidities=as_series["humidities"],
        timestamps=as_series["timestamps"],
    )


if __name__ == "__main__":
    app.run(debug=True)
