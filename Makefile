.PHONY: build check test eval
build:
	python3 scripts/build.py
check: build
	python3 scripts/check.py
	node --check site/site.js
test:
	python3 -B -m unittest discover -s tests -v
eval:
	python3 evals/run.py --validate
