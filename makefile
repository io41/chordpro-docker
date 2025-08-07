build:
	docker build -t chordpro-api .

build-dev:
	docker build -f Dockerfile.dev -t chordpro-api:dev .

# DEPRECATED: Use run-api-auth instead
run-api:
	@echo "ERROR: Direct run-api is disabled for security."
	@echo "Use one of:"
	@echo "  API_KEYS='your-key' make run-api-auth  # Production with authentication"
	@echo "  make run-api-dev                       # Development mode"
	@echo "  make run-api-unsafe                    # Development mode override"
	@exit 1

# Run development server (no authentication)
run-api-dev:
	docker run \
	--rm \
	-p 8080:8080 \
	--name chordpro-api-dev \
	chordpro-api:dev

# Run with API keys - REQUIRED for production
run-api-auth:
	@if [ -z "${API_KEYS}" ]; then \
		echo "ERROR: API_KEYS environment variable is required"; \
		echo "Usage: API_KEYS='your-key-here' make run-api-auth"; \
		exit 1; \
	fi
	docker run \
	--rm \
	-p 8080:8080 \
	--name chordpro-api \
	-e API_KEYS="${API_KEYS}" \
	chordpro-api

# Development mode with explicit override (not recommended)
run-api-unsafe:
	@echo "WARNING: Running in development mode without authentication!"
	docker run \
	--rm \
	-p 8080:8080 \
	--name chordpro-api \
	-e DEVELOPMENT_MODE=true \
	chordpro-api

# Run the original CLI (for backwards compatibility)
run-cli:
	docker run \
	--rm \
	-v `pwd`:`pwd` \
	-w `pwd` \
	--entrypoint chordpro \
	chordpro-api \
	${args}

# Stop the API server
stop:
	docker stop chordpro-api 2>/dev/null || true

# Build and run in development mode
dev: build-dev run-api-dev
