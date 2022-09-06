all:
	rm -f build/confluence-quicksearch.alfredworkflow
	mkdir -p build
	cd src && zip -qR confluence-quicksearch.alfredworkflow "*"
	mv src/confluence-quicksearch.alfredworkflow build
