# ChordPro Web API

Production-ready REST API wrapper for the [ChordPro](https://chordpro.org) CLI utility. Convert ChordPro format songs to PDF, HTML, text, and other formats via HTTP requests.

## Quick Start

### Production (Secure by Default)
```bash
docker run -d -p 8080:8080 \
  -e API_KEYS="your-secure-api-key-here" \
  --name chordpro-api \
  io41/chordpro-api:latest
```

### Development (No Authentication)
```bash
docker run -d -p 8080:8080 \
  --name chordpro-api-dev \
  io41/chordpro-api:dev
```

Visit `http://localhost:8080/` for interactive API documentation.

## Features

- ✅ **Secure by default** - API keys required, refuses to start without them
- ✅ **Multiple formats** - PDF, HTML, text, ChordPro output
- ✅ **Built-in configurations** - Ukulele, guitar, modern themes, and more
- ✅ **Production ready** - Gunicorn WSGI server, comprehensive logging
- ✅ **Interactive docs** - Web interface with usage examples
- ✅ **Multi-architecture** - Supports linux/amd64 and linux/arm64

## Available Tags

- `latest` - Latest stable production release
- `v1.0.0` - Specific version tags
- `dev` - Development version (no authentication)

## Basic API Usage

```bash
# Convert ChordPro to PDF
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "content": "{title: My Song}\n\n[C]Hello [G]world [Am]here",
    "options": {"config": "ukulele,modern3"}
  }' \
  --output song.pdf
```

## Configuration Examples

- **Ukulele + Modern styling**: `"config": "ukulele,modern3"`
- **Guitar (default)**: `"config": "guitar"`
- **Keyboard notation**: `"config": "keyboard"`
- **Transpose**: `"transpose": 2` (semitones)
- **Add metadata**: `"meta": {"artist": "Artist Name"}`

## Environment Variables

### Production (Required)
- `API_KEYS` - Comma-separated API keys (e.g., `"key1,key2,key3"`)

### Development (Optional Override)
- `DEVELOPMENT_MODE=true` - Disable authentication (not recommended)

## Multi-Architecture Support

This image supports multiple architectures:
- `linux/amd64` - Intel/AMD 64-bit
- `linux/arm64` - ARM 64-bit (Apple Silicon, ARM servers)

Docker will automatically pull the correct architecture for your platform.

## Security Features

- **Timing attack protection** - Uses `hmac.compare_digest()` for API key comparison
- **Input validation** - Content size limits, type checking
- **Security headers** - XSS, clickjacking protection
- **Error sanitization** - No sensitive information disclosure
- **Process isolation** - Container-based security

## Links

- **Documentation**: [GitHub Repository](https://github.com/user/chordpro-docker)
- **ChordPro Project**: [chordpro.org](https://chordpro.org)
- **Issues & Support**: [GitHub Issues](https://github.com/user/chordpro-docker/issues)

## License

This project follows ChordPro's licensing. The Docker wrapper is provided as-is for convenience.