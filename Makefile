
test-version:
	python3 setup.py sdist && python3 -m twine upload --repository testpypi --skip-existing dist/*

version:
	python3 setup.py sdist && python3 -m twine upload --skip-existing dist/*
migration:
	cp migrations/migration.py.stub migrations/$$(date +%s).py
