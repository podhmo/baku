test:
	pytest -vv --show-capture=all

ci:
	pytest --show-capture=all --cov=baku --no-cov-on-fail --cov-report term-missing
	$(MAKE) lint typing

format:
#	pip install -e .[dev]
	black baku setup.py

# https://www.flake8rules.com/rules/W503.html
# https://www.flake8rules.com/rules/E203.html
# https://www.flake8rules.com/rules/E501.html
lint:
#	pip install -e .[dev]
	flake8 baku --ignore W503,E203,E501

typing:
#	pip install -e .[dev]
	mypy --strict --strict-equality --ignore-missing-imports baku
mypy: typing

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/baku-$(shell cat VERSION)*
	twine upload dist/baku-$(shell cat VERSION)*

examples:
	$(MAKE) -C examples
.PHONY: examples

.PHONY: test ci format lint typing mypy build upload
