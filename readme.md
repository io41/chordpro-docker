# ChordPro Docker

This repository contains a Dockerfile
for creating a docker image with the
[chordpro](https://chordpro.org) cli utility
available.

## Building

Build the docker image.

```bash
docker build -t chordpro .
```

Or use the make command:

```bash
make build
```

## Usage

For use the same way as the cli utility
you need to pass in the current directory
along with setting in as a working directory
inside the container:

```bash
docker run \
	--rm \
	-v `pwd`:`pwd` \
	-w `pwd` \
	chordpro \
    song.cho \
    -o song.pdf
```

Or use the `make run` command like so:

```bash
make run args="song.cho -o song.pdf"
```

Information about the CLI options can be found [here](https://chordpro.org/chordpro/using-chordpro/).
