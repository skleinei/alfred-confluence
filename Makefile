all:
	rm -f build/alfred-confluence.alfredworkflow
	mkdir -p build
	python -m compileall -b .
	cd src && zip -qR alfred-confluence.alfredworkflow "*"
	mv src/alfred-confluence.alfredworkflow build
