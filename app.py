import os
import time
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(message="Hello from Kubernetes", pod=os.getenv("HOSTNAME", "local"))


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/cpu")
def cpu():
    # Burns CPU for ~0.2s so you can trigger the autoscaler with a load test.
    end = time.time() + 0.2
    while time.time() < end:
        sum(i * i for i in range(1000))
    return jsonify(status="busy")
