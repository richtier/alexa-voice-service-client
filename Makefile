clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

build:
	rm -rf build
	rm -rf dist
	python setup.py bdist_wheel


publish_test:
	make build
	twine upload -r pypitest dist/*


publish:
	make build
	twine upload dist/*


test_requirements:
	pip install -e .[test]


.PHONY: build publish_test publish test_requirements
