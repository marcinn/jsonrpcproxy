.DEFAULT_GOAL = install
.PHONY = install

env:
	python -m venv env


clean:
	rm -rf dist/ .eggs/ *.egg-info/


install: env
	./env/bin/pip install pip
	./env/bin/pip install -e .[dev]


package: clean install
	./env/bin/python -m build


upload: clean package
	./env/bin/twine upload dist/*


