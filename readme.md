# ChordPro Web API

This repository provides a Web API wrapper for the [ChordPro](https://chordpro.org) CLI utility, packaged as a Docker container. The API allows you to convert ChordPro format files to PDF, HTML, text, and other formats via HTTP requests.

**Docker Hub**: [`io41/chordpro-api`](https://hub.docker.com/r/io41/chordpro-api)

## Features

- **RESTful API** for ChordPro conversions
- **Multiple output formats**: PDF, HTML, text, ChordPro
- **Built-in configurations**: Ukulele, guitar, modern themes, and more
- **CLI options support**: Transpose, metadata, chord diagrams, configurations
- **API key authentication** with environment variable support
- **Interactive documentation** via web interface
- **Extensible architecture** for future ChordPro features
- **Health checks** and error handling
- **Backwards compatibility** with original CLI usage

## Quick Start

### Quick Start with Docker Hub

```bash
# PRODUCTION (Secure by default - API keys required):
docker run -d -p 8080:8080 \
  -e API_KEYS="your-secure-api-key-here" \
  --name chordpro-api \
  io41/chordpro-api:latest

# DEVELOPMENT (No authentication):
docker run -d -p 8080:8080 \
  --name chordpro-api-dev \
  io41/chordpro-api:dev
```

### Build from Source

```bash
# Build the Docker image locally
make build

# PRODUCTION (Secure by default - API keys required):
API_KEYS="your-secure-api-key-here" make run-api-auth

# DEVELOPMENT (No authentication):
make build-dev && make run-api-dev
```

The API will be available at `http://localhost:8080`

**Visit `http://localhost:8080/` for interactive API documentation.**

### Basic Usage

Convert ChordPro text to PDF:

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Amazing Grace}\n\n[C]Amazing grace how [F]sweet the [C]sound"
  }' \
  --output song.pdf
```

## API Endpoints

- `GET /health` - Health check
- `GET /formats` - List supported output formats  
- `GET /options` - List supported CLI options
- `POST /convert` - Convert ChordPro content

## Supported Features

### Output Formats
- **PDF** (default) - High-quality printable format
- **HTML** - Web-ready format with styling
- **Text** - Plain text output
- **ChordPro** - Normalized ChordPro format

### CLI Options
- **Transpose** - Change key by semitones
- **Metadata** - Add title, artist, album, etc.
- **Chord diagrams** - Include/exclude chord charts

## Examples

See [API_EXAMPLES.md](API_EXAMPLES.md) for comprehensive usage examples including:
- Basic conversions
- Advanced options (transpose, metadata)
- Different output formats  
- Error handling
- Integration scripts

## CLI Compatibility

The original CLI functionality is still available:

```bash
# Run ChordPro CLI directly
make run-cli args="song.cho -o song.pdf"

# Or manually:
docker run --rm -v `pwd`:`pwd` -w `pwd` --entrypoint chordpro chordpro-api song.cho -o song.pdf
```

## Architecture

The Web API is built with:
- **Flask** - Lightweight Python web framework
- **ChordProProcessor** - Modular CLI wrapper class
- **Extensible design** - Easy to add new ChordPro options
- **Temporary file handling** - Secure processing pipeline
- **Error handling** - Proper HTTP status codes

## Development

```bash
# Build and run in development mode
make dev

# Stop the API server
make stop
```

For more information about ChordPro CLI options, visit the [official documentation](https://chordpro.org/chordpro/using-chordpro/).