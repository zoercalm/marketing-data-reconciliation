demo:
	python3 generate.py
	python3 reconcile.py fixtures/expected.csv fixtures/matching.csv
test:
	python3 -m unittest -v
