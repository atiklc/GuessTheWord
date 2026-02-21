from flask import Flask, send_from_directory

app = Flask(__name__)


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.get("/<path:path>")
def static_files(path: str):
    return send_from_directory(".", path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
