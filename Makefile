deploy:
	stickytape "scripts/knowledge/model/association/basic/__main__.py" \
		--add-python-path "scripts/" \
		--output-file "deploy/basic_association.py"

build:
	python setup.py

install:
	pip install ./

setup:
	pip install requirements.txt

clean:
	rm *.egg-info
	rm -r build/
	rm -r dist/
	rm deploy/*
