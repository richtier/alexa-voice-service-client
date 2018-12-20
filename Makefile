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


test:
	flake8 --exclude=.venv,venv,snowboy,build,**/fixtures.py
	pytest --ignore=build --ignore=venv --ignore=.venv --cov=./ --cov-config=.coveragerc --last-failed


.PHONY: build publish_test publish test_requirements test
