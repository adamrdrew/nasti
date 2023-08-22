test:
	python -m unittest discover .

coverage:
	coverage run -m unittest discover .
	coverage report -m
	coverage xml

sync-deps:
	python3 sync_deps.py

# Don't run these in the venv
# It took a lot of trial and error and I'm not sure
# but I don't think this works right in a venv
install-build-deps:
	pip install build twine wheel
build-app: sync-deps
	rm -rf build dist *.egg-info
	python -m build
publish:
	python -m twine upload dist/*