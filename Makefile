help:
	@echo "TODO: Write the install help"

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

install:
	pip install -Ur requirements_dev.txt
	pip install -Ur requirements.txt -t ./external
	@echo "Requirements installed."


unit:
	nosetests -sv -a is_unit --with-gae --gae-application=./tests/app.yaml  --gae-lib-root=$(GAE_PYTHONPATH) --with-yanc --logging-level=ERROR tests
