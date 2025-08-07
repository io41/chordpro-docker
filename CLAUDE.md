# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker containerization project for the ChordPro CLI utility. ChordPro is a tool for processing chord sheets and songbooks. The project creates a minimal Docker image that packages the chordpro command-line tool for easy distribution and usage.

## Architecture

The project is extremely simple with just 4 main files:

- **Dockerfile**: Ubuntu-based image that installs chordpro via apt-get
- **makefile**: Provides build and run convenience commands
- **readme.md**: User documentation with build and usage examples
- **LICENSE**: Project licensing

The Docker image uses Ubuntu rolling as base and installs chordpro through the system package manager, making it a thin wrapper around the existing chordpro package.

## Common Commands

### Building the Docker image
```bash
make build
# or manually:
docker build -t chordpro-api .
```

### Running the Web API
```bash
make run-api
# or manually:
docker run --rm -p 8080:8080 --name chordpro-api chordpro-api
```

### Running ChordPro CLI (backwards compatibility)
```bash
make run-cli args="input.cho -o output.pdf"
# or manually:
docker run --rm -v `pwd`:`pwd` -w `pwd` --entrypoint chordpro chordpro-api input.cho -o output.pdf
```

### Development
```bash
make dev          # Build and run API server
make stop         # Stop the API server
```

### Testing
Test the API manually:
```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/convert -H "Content-Type: application/json" -d '{"content": "[C]Hello world"}' --output test.pdf
```

## Web API Architecture

The project now includes a Flask-based Web API (`app.py`) that wraps the ChordPro CLI:

- **ChordProProcessor class**: Modular wrapper for CLI operations
- **RESTful endpoints**: `/health`, `/formats`, `/options`, `/convert`
- **Extensible design**: Easy to add new ChordPro CLI options
- **Temporary file handling**: Secure processing with cleanup
- **Multiple output formats**: PDF, HTML, text, ChordPro

Key files:
- `app.py`: Flask web server and ChordPro processor
- `requirements.txt`: Python dependencies
- `API_EXAMPLES.md`: Comprehensive usage examples

## Development Notes

- The Web API accepts ChordPro content via JSON POST requests
- Temporary files are created in `/tmp` and cleaned up automatically  
- CLI options are mapped to JSON parameters for easy expansion
- Error handling returns appropriate HTTP status codes
- Volume mounting is only needed for CLI compatibility mode