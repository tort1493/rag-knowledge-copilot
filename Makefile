.PHONY: setup lint test train eval serve docker-build docker-run

setup:
\tpython -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

lint:
\truff check .
\tpython -m compileall src

test:
\tpytest -q

train:
\tpython scripts/train.py

eval:
\tpython scripts/eval.py

serve:
\tuvicorn infra.api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
\tdocker build -t ai-project .

docker-run:
\tdocker run -p 8000:8000 ai-project
