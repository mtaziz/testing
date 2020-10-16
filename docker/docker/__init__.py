import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

directory = "logs"
parent_dir = BASE_DIR
path = os.path.join(parent_dir, directory)
os.makedirs(path, exist_ok=True)

directory = str(datetime.utcnow().date())
parent_dir = path
path = os.path.join(parent_dir, directory)
os.makedirs(path, exist_ok=True)
