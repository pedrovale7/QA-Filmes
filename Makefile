PIP = pip
PYTHON = python3
init: 
	$(PIP) install -r requirements.txt
	$(PYTHON) back-end/vetorizacao.py