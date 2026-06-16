.PHONY: venv install run clean

venv:
	python3 -m venv .venv

install: venv
	. .venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

run:
	. .venv/bin/activate && \
	python treasure_dash.py

clean:
	rm -rf .venv
