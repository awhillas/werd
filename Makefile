requirements:
	# See: https://hynek.me/til/pip-tools-and-pyproject-toml/
	python -m pip install --upgrade pip-tools pip wheel
	python -m piptools compile --upgrade --resolver backtracking -o requirements/main.txt pyproject.toml
	python -m piptools compile --extra dev --upgrade --resolver backtracking -o requirements/dev.txt pyproject.toml


init:
	rm -rf .tox
	python -m pip install --upgrade pip wheel
	python -m pip install --upgrade -r requirements/main.txt -r requirements/dev.txt -e .
	python -m pip check

update: requirements init

.PHONY: requirements init update
