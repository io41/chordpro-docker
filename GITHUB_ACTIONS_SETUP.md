# GitHub Actions Setup Guide

## Required Repository Secrets

Before the workflows can run, you need to add these secrets to your GitHub repository:

### 1. Go to Repository Settings
- Navigate to your repository on GitHub
- Click **Settings** → **Secrets and variables** → **Actions**

### 2. Add Required Secrets

Click **New repository secret** and add:

#### `DOCKERHUB_USERNAME`
- **Value**: `io41` (your Docker Hub username)

#### `DOCKERHUB_TOKEN` 
- **Value**: Your Docker Hub access token
- **How to create**:
  1. Go to https://hub.docker.com/settings/security
  2. Click **New Access Token**
  3. Name: `GitHub Actions`
  4. Permissions: **Read, Write, Delete**
  5. Copy the token (you'll only see it once!)

## Workflow Overview

### 1. **docker-build.yml** - Main Build Workflow
**Triggers:**
- Push to `main` or `develop` branches
- Tags starting with `v*` (e.g., `v1.0.1`)
- Pull requests to `main`

**What it does:**
- ✅ Builds both production and development Docker images
- ✅ Supports multi-architecture: `linux/amd64` and `linux/arm64`
- ✅ Pushes to Docker Hub (production only, not on PRs)
- ✅ Runs security vulnerability scans with Trivy
- ✅ Tests images before pushing
- ✅ Uses Docker layer caching for faster builds

### 2. **release.yml** - Release Workflow  
**Triggers:**
- Git tags starting with `v*` (e.g., `git tag v1.0.1 && git push --tags`)

**What it does:**
- ✅ Creates GitHub releases automatically
- ✅ Updates Docker Hub repository description
- ✅ Generates release notes with usage examples

### 3. **dependabot-auto-merge.yml** - Dependency Management
**Triggers:**
- Dependabot pull requests

**What it does:**
- ✅ Auto-merges low-risk dependency updates
- ✅ Keeps the project secure and up-to-date

## Image Tags Created

### On `main` branch push:
- `io41/chordpro-api:latest` (production)
- `io41/chordpro-api:main` (production)
- `io41/chordpro-api:dev` (development)
- `io41/chordpro-api:dev-<commit-sha>`

### On version tag (e.g., `v1.0.1`):
- `io41/chordpro-api:v1.0.1` (exact version)
- `io41/chordpro-api:1.0.1` (without 'v')
- `io41/chordpro-api:1.0` (major.minor)
- `io41/chordpro-api:1` (major only)
- `io41/chordpro-api:latest` (updated)

### On `develop` branch push:
- `io41/chordpro-api:develop`

## Testing

The workflows include comprehensive testing:

### Build-time Tests
- ✅ Docker image builds successfully
- ✅ Multi-architecture support verified
- ✅ Application starts without errors

### Runtime Tests  
- ✅ Health endpoint responds correctly
- ✅ Production mode requires API keys
- ✅ Development mode works without auth

### Security Tests
- ✅ Trivy vulnerability scanning
- ✅ SARIF results uploaded to GitHub Security tab

## Creating a Release

To create a new release:

```bash
# Tag the release
git tag v1.0.1

# Push the tag
git push origin v1.0.1
```

This will:
1. Trigger the build workflow
2. Build and push multi-arch images  
3. Create a GitHub release
4. Update Docker Hub description

## Status Badges

Add these to your README.md:

```markdown
[![Docker Build](https://github.com/yourusername/chordpro-docker/actions/workflows/docker-build.yml/badge.svg)](https://github.com/yourusername/chordpro-docker/actions/workflows/docker-build.yml)
[![Docker Hub](https://img.shields.io/docker/pulls/io41/chordpro-api)](https://hub.docker.com/r/io41/chordpro-api)
[![Security Scan](https://github.com/yourusername/chordpro-docker/actions/workflows/docker-build.yml/badge.svg?event=schedule)](https://github.com/yourusername/chordpro-docker/actions/workflows/docker-build.yml)
```

## Troubleshooting

### Common Issues:

1. **"docker/login-action failed"**
   - Check `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
   - Verify Docker Hub token has write permissions

2. **"Build failed: permission denied"**  
   - Check repository permissions in GitHub Actions settings
   - Ensure secrets are available to workflows

3. **"Multi-arch build failed"**
   - This is normal for complex builds, the action will retry
   - Check if ChordPro packages are available for ARM64

### Debug Mode

To enable debug logging, add this secret:
- `ACTIONS_STEP_DEBUG`: `true`

This will show detailed logs for troubleshooting build issues.

## Security Considerations

- ✅ Docker Hub tokens are stored as encrypted secrets
- ✅ Images are scanned for vulnerabilities before push  
- ✅ SARIF results are uploaded to GitHub Security tab
- ✅ Dependabot keeps dependencies updated automatically
- ✅ Multi-architecture support reduces supply chain risks