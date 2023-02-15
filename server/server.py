from flask import Flask
from config import Config

app = Flask(__name__, static_folder="../client")
app.config.from_object(Config)

import routes