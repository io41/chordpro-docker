build:
	docker build -t chordpro .

run:
	docker run \
	--rm \
	-v `pwd`:`pwd` \
	-w `pwd` \
	chordpro \
	${args}
