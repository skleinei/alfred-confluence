version = v2.1.0-beta

all:
	rm -f build/confluence-*.alfredworkflow
	mkdir -p build
	cd src && zip -qR confluence-${version}.alfredworkflow "*"
	mv src/confluence-${version}.alfredworkflow build

install:
	rm -f build/confluence-*.alfredworkflow
	mkdir -p build
	cd src && zip -qR confluence-${version}.alfredworkflow "*"
	mv src/confluence-${version}.alfredworkflow build
	open build/confluence-${version}.alfredworkflow