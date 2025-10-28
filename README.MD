Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate

Install all dependencies from requirements.txt:
pip install --upgrade pip
pip install -r requirements.txt

Run the project (app/main.py): python3 main.py
or (/Timeline): ./start.sh

For the tests:
Install pytest (from requirements.txt):

pip install pytest

Run the tests (Tests/test_basic_entities.py):

python3 -m pytest Tests/test_basic_entities.py -v