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


lint:
	flake8 --exclude=.venv,venv,snowboy,build


test:
	pytest $1 \
		--ignore=venv \
		--ignore=.venv \
		--ignore=build \
		--cov=./ \
		--cov-config=.coveragerc \
		--capture=no \
		--last-failed \
		-vv

.PHONY: build publish_test publish test_requirements test
