development:
	tox -e venv

.PHONY: clean
clean:
	find -name '*.pyc' -delete
	find -name '__pycache__' -delete

.PHONY: purge
purge:
	find -name '.tox' | xargs --no-run-if-empty rm -r
	find -name '*.egg-info' | xargs --no-run-if-empty rm -r

.PHONY: vulnerable_app
vulnerable_app:
	python -m testing.vulnerable_app
