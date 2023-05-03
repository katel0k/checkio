import sys

# args = {arg.split('=')[0]: arg.split('=')[1] for arg in sys.argv[1:]}
args = {}
from .application import create_app
app = create_app(**args)

from .routes import *