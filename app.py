from flask import Flask, render_template
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('pages/home.html')


if __name__ == '__main__':
    host = os.getenv("APP_HOST")
    port = os.getenv("APP_PORT")
    debug = os.getenv("APP_DEBUG")

    app.run(host=host, port=port, debug=debug)
