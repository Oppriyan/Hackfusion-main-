import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)