all:
	rm -f build/alfred-confluence.alfred3workflow
	mkdir -p build
	zip -qR build/alfred-confluence.alfred3workflow "*"

