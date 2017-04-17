all:
	rm -f build/alfred-confluence.alfred3workflow
	mkdir -p build
	cd src && zip -qR alfred-confluence.alfred3workflow "*"
	mv src/alfred-confluence.alfred3workflow build

