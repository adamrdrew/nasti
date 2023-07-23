test:
	python -m unittest discover .

coverage:
	coverage run -m unittest discover .
	coverage report -m
	coverage xml