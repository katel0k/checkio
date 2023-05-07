import sys

args = {}
from .application import create_app
app = create_app(**args)

from .routes import *