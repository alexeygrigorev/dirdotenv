.PHONY: test build check publish-test publish clean clean-build

# Run tests
test:
	uv run pytest

publish-build:
	uv run hatch build

publish-test:
	uv run hatch publish --repo test

publish:
	uv run hatch publish

publish-clean:
	rm -r dist/