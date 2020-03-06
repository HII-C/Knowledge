
build:
	stickytape "scripts/knowledge/model/association/basic/__main__.py" \
		--add-python-path "scripts/" \
		--output-file "deploy/basic_association.py"

test:
	

install:
	pip install ./

setup:
	pip install requirements.txt

clean:
	rm *.egg-info
	rm -r build/
	rm -r dist/
