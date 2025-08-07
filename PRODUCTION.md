# Production Deployment Guide

## Production vs Development

### Production (Default)
- **Server**: Gunicorn WSGI server with 2 workers
- **Logging**: Structured logging with timestamps and levels
- **Security**: Security headers, input validation, error sanitization
- **Monitoring**: Enhanced health check with ChordPro availability
- **Performance**: Request timeout (30s), file cleanup, process limits

### Development
- **Server**: Flask development server
- **Build**: `make build-dev` and `make run-api-dev`
- **Purpose**: Local testing and development only

## Security-First Design

**⚠️ SECURE BY DEFAULT**: The container **will refuse to start** without API keys in production mode.

## Quick Production Start

```bash
# Using Docker Hub image (recommended)
docker run -d -p 8080:8080 \
  -e API_KEYS="your-secure-key-here" \
  --name chordpro-api \
  io41/chordpro-api:latest

# Or build from source
make build
API_KEYS="your-secure-key-here" make run-api-auth
```

## Development Mode

```bash
# Development mode (explicit override)
make build-dev && make run-api-dev

# Or with production image but development mode
docker run -e DEVELOPMENT_MODE=true chordpro-api
```

## Environment Variables

### API_KEYS (Required for Production)
```bash
# Multiple keys (comma-separated)
API_KEYS="client-key-1,admin-key-2,service-key-3"

# Individual keys
API_KEY_1="client-key"
API_KEY_2="admin-key"
```

**Security Recommendations:**
- Use keys ≥16 characters (warnings logged for shorter keys)
- Generate cryptographically random keys (use `openssl rand -base64 32`)
- Rotate keys regularly
- Use different keys per environment/client

**Timing Attack Protection:**
- API key comparison uses `hmac.compare_digest()` for constant-time comparison
- Prevents timing-based API key enumeration attacks

## Production Configuration

### Resource Limits
- **Content Size**: 1MB limit per request
- **Request Timeout**: 30 seconds
- **Workers**: 2 Gunicorn workers (configurable in `gunicorn.conf.py`)
- **Memory**: ~100MB per worker + ChordPro overhead

### Security Features
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Request validation and sanitization
- Error message sanitization (no path disclosure)
- API key authentication
- Process isolation via containers

### Monitoring
- **Health Check**: `GET /health`
  - Verifies ChordPro availability
  - Returns service status and timestamp
  - Used by Docker healthcheck
- **Logging**: Structured JSON-like logs to stdout
  - Request/response logging
  - Error tracking with severity levels
  - Authentication attempt logging

## Production Checklist

- [ ] Set strong API keys via `API_KEYS` environment variable
- [ ] Monitor logs for warnings/errors
- [ ] Set up log aggregation (stdout logs)
- [ ] Configure reverse proxy (nginx/Traefik) if needed
- [ ] Set up monitoring/alerting for `/health` endpoint
- [ ] Configure backup/restore for any persistent data
- [ ] Test API key rotation process
- [ ] Verify HTTPS termination at load balancer/proxy

## Sample Production Docker Compose

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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 128M
```

## Security Considerations

### MVP Security Features ✅
- **Secure by default**: Requires API keys, refuses to start without them
- **Timing attack protection**: Uses `hmac.compare_digest()` for API key comparison
- **API key authentication** with environment variable support
- **Input validation** and size limits (1MB max)
- **Process timeout** protection (30s max)
- **Error message sanitization** (no path disclosure)
- **Security headers** (XSS, clickjacking, content sniffing protection)
- **Structured logging** with security event tracking

### Additional Security (Future)
- Rate limiting per client
- Request signing/HMAC
- IP allowlisting
- Audit logging
- Request/response encryption

## Performance Notes

- **Concurrent requests**: 2 workers handle ~1000 concurrent connections
- **Processing time**: ~1-3 seconds per conversion (varies by content)
- **Memory usage**: ~50-100MB per active conversion
- **Scaling**: Increase Gunicorn workers or run multiple containers

## Troubleshooting

### Common Issues
1. **ChordPro not available**: Check health endpoint
2. **Authentication failures**: Verify API_KEYS environment variable
3. **Large file failures**: Check 1MB content limit
4. **Timeout errors**: Complex songs may take longer to process

### Log Analysis
```bash
# View logs
docker logs chordpro-api

# Follow logs
docker logs -f chordpro-api

# Filter errors
docker logs chordpro-api 2>&1 | grep ERROR
```