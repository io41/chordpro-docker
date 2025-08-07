# ChordPro Web API v1.0.0 Release

## Docker Hub Images

**Production Image**: `io41/chordpro-api:latest` or `io41/chordpro-api:v1.0.0`  
**Development Image**: `io41/chordpro-api:dev`

## Quick Start

```bash
# PRODUCTION (Secure by default)
docker run -d -p 8080:8080 \
  -e API_KEYS="your-secure-api-key-here" \
  --name chordpro-api \
  io41/chordpro-api:latest

# DEVELOPMENT (No authentication)
docker run -d -p 8080:8080 \
  --name chordpro-api-dev \
  io41/chordpro-api:dev
```

## Features

### ✅ **Core Functionality**
- **ChordPro → PDF conversion** with high-quality output
- **Multiple formats**: PDF, HTML, text, ChordPro
- **Built-in configurations**: `ukulele,modern3`, `guitar`, `keyboard`, etc.
- **CLI options**: Transpose, metadata, chord diagrams
- **Interactive web documentation** at `/`

### ✅ **Security (Production Ready)**
- **Secure by default**: Container refuses to start without API keys
- **Timing attack protection**: Uses `hmac.compare_digest()` for API key comparison
- **Input validation**: 1MB content limits, type checking
- **Security headers**: XSS, clickjacking, content sniffing protection
- **Error sanitization**: No sensitive information disclosure

### ✅ **Production Features**
- **Gunicorn WSGI server** with multi-worker support
- **Structured logging** with timestamps and security events
- **Health checks** with ChordPro availability verification
- **Process timeouts** (30s) and resource management
- **Auto-cleanup** of temporary files

## API Usage

### Authentication
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8080/convert
```

### Basic Conversion
```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "content": "{title: My Song}\n\n[C]Hello [G]world",
    "options": {"config": "ukulele,modern3"}
  }' \
  --output song.pdf
```

## Deployment Options

### Docker Compose
```yaml
version: '3.8'
services:
  chordpro-api:
    image: io41/chordpro-api:latest
    ports:
      - "8080:8080"
    environment:
      - API_KEYS=${API_KEYS}
    restart: unless-stopped
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chordpro-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chordpro-api
  template:
    metadata:
      labels:
        app: chordpro-api
    spec:
      containers:
      - name: chordpro-api
        image: io41/chordpro-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: API_KEYS
          valueFrom:
            secretKeyRef:
              name: chordpro-secrets
              key: api-keys
```

## Architecture

- **Base**: Ubuntu rolling with ChordPro system package
- **Runtime**: Python 3.13 with Gunicorn WSGI server
- **Size**: ~1.67GB (includes full ChordPro dependencies)
- **Memory**: ~100-200MB per worker process
- **Processing**: 1-3 seconds per conversion (varies by complexity)

## Security Model

### MVP Security Features
- ✅ **Secure by default** - requires API keys
- ✅ **Timing attack protection**
- ✅ **Input validation and sanitization**
- ✅ **Security headers and error handling**
- ✅ **Process isolation via containers**
- ✅ **Comprehensive logging**

### Environment Modes
- **Production** (default): API keys required, Gunicorn server, full security
- **Development**: `DEVELOPMENT_MODE=true`, Flask dev server, no auth

## Version History

### v1.0.0 (2025-08-07)
- Initial production release
- Full ChordPro CLI wrapper with Web API
- Secure by default with API key authentication
- Production-ready with Gunicorn and comprehensive security
- Support for all major ChordPro configurations (ukulele, modern3, etc.)
- Interactive documentation website
- Docker Hub images available

## Support

- **Documentation**: See `README.md`, `PRODUCTION.md`, `API_EXAMPLES.md`
- **Docker Hub**: https://hub.docker.com/r/io41/chordpro-api
- **ChordPro Docs**: https://chordpro.org/chordpro/using-chordpro/

## License

This project follows the same licensing as ChordPro itself. See `LICENSE` file for details.