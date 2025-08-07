# ChordPro Web API Usage Examples

## Starting the API Server

```bash
# Build the Docker image
docker build -t chordpro-api .

# Run without authentication (development mode)
docker run --rm -p 8080:8080 --name chordpro-api chordpro-api

# Run with API key authentication
docker run --rm -p 8080:8080 --name chordpro-api \
  -e API_KEYS="your-api-key,another-key" \
  chordpro-api

# Or use make commands
make build
make run-api                    # Development mode (no auth)
API_KEYS="key1,key2" make run-api-auth  # With authentication
```

## Authentication

When API keys are configured, include the `X-API-Key` header in your requests:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8080/formats
```

**Note**: The index page (`/`) and health check (`/health`) endpoints don't require authentication.

## API Endpoints

### Health Check

```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "chordpro-api"
}
```

### Get Supported Formats

```bash
curl http://localhost:8080/formats
```

**Response:**
```json
{
  "supported_formats": ["pdf", "text", "cho", "html"],
  "default_format": "pdf"
}
```

### Get Supported Options

```bash
curl http://localhost:8080/options
```

**Response:**
```json
{
  "supported_options": {
    "transpose": {
      "type": "integer",
      "description": "Transpose by semitones"
    },
    "meta": {
      "type": "object",
      "description": "Metadata key-value pairs"
    },
    "diagrams": {
      "type": "boolean",
      "description": "Include chord diagrams"
    },
    "config": {
      "type": "string",
      "description": "Configuration file path (future)"
    }
  }
}
```

## Convert ChordPro to PDF (Basic)

**Note**: Add `-H "X-API-Key: your-api-key"` to all curl commands when authentication is enabled.

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Amazing Grace}\n{subtitle: Traditional}\n\n{start_of_chorus}\nAma[C]zing grace how [F]sweet the [C]sound\nThat [C]saved a wretch like [G]me\nI [C]once was lost but [F]now I am [C]found\nWas [Am]blind but [G]now I [C]see\n{end_of_chorus}"
  }' \
  --output amazing_grace.pdf
```

## Convert with Options

### Transpose Song

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Amazing Grace}\n\n[C]Amazing grace how [F]sweet the [C]sound",
    "output_format": "pdf",
    "options": {
      "transpose": 2
    }
  }' \
  --output transposed_song.pdf
```

### Add Metadata

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "[C]Amazing grace how [F]sweet the [C]sound",
    "output_format": "pdf",
    "options": {
      "meta": {
        "title": "Amazing Grace",
        "artist": "Traditional",
        "album": "Hymns Collection"
      }
    }
  }' \
  --output song_with_meta.pdf
```

### Disable Chord Diagrams

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Simple Song}\n\n[C]Hello [G]world [Am]song [F]here",
    "output_format": "pdf",
    "options": {
      "diagrams": false
    }
  }' \
  --output no_diagrams.pdf
```

### Use ChordPro Configurations

#### Single Configuration
```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Ukulele Song}\n\n[C]Amazing [F]grace how [C]sweet",
    "output_format": "pdf",
    "options": {
      "config": "ukulele"
    }
  }' \
  --output ukulele_song.pdf
```

#### Multiple Configurations (Comma-Separated)
```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Modern Ukulele Song}\n\n[C]Hello [G]world [Am]here",
    "output_format": "pdf",
    "options": {
      "config": "ukulele,modern3"
    }
  }' \
  --output modern_ukulele.pdf
```

#### Multiple Configurations (Array Format)
```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Array Config Song}\n\n[D]Test [A]song [G]here",
    "output_format": "pdf",
    "options": {
      "config": ["guitar", "modern2"]
    }
  }' \
  --output array_config.pdf
```

**Available built-in configurations:**
- `ukulele` - Ukulele-specific chord diagrams and tuning
- `guitar` - Guitar configurations (default)
- `modern1`, `modern2`, `modern3` - Modern styling variants
- `keyboard` - Keyboard/piano chord notation
- `mandolin-ly` - Mandolin configurations
- `nashville` - Nashville number system
- `roman` - Roman numeral notation
- `dark` - Dark theme styling

## Convert to Other Formats

### Convert to Plain Text

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Test Song}\n\n[C]Hello [G]world",
    "output_format": "text"
  }' \
  --output song.txt
```

### Convert to HTML

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Test Song}\n\n[C]Hello [G]world",
    "output_format": "html"
  }' \
  --output song.html
```

### Convert to ChordPro Format (Normalized)

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: Test Song}\n\n[C]Hello [G]world",
    "output_format": "cho"
  }' \
  --output normalized.cho
```

## Complex Example

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{title: House of the Rising Sun}\n{subtitle: Traditional}\n{key: Am}\n\nThere [Am]is a [C]house in [D]New Or[F]leans\nThey [Am]call the [C]Rising [E7]Sun\nAnd it has [Am]been the [C]ruin of [D]many a poor [F]boy\nAnd [Am]God I [E7]know I am [Am]one",
    "output_format": "pdf",
    "options": {
      "transpose": -2,
      "config": "ukulele,modern3",
      "meta": {
        "genre": "Folk",
        "tempo": "120 BPM"
      },
      "diagrams": true
    }
  }' \
  --output complex_ukulele_song.pdf
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful conversion
- `400 Bad Request`: Invalid input or missing required fields  
- `500 Internal Server Error`: ChordPro processing failed

Example error response:
```json
{
  "error": "ChordPro processing failed: Invalid chord syntax"
}
```

## Using with Scripts

### Bash Script Example

```bash
#!/bin/bash

# Convert multiple ChordPro files via API
for file in *.cho; do
  echo "Converting $file..."
  
  curl -X POST http://localhost:8080/convert \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"$(cat "$file" | sed 's/"/\\"/g')\"}" \
    --output "${file%.cho}.pdf"
done
```

### Python Script Example

```python
import requests
import json

def convert_chordpro(content, output_format='pdf', options=None):
    url = 'http://localhost:8080/convert'
    
    payload = {
        'content': content,
        'output_format': output_format,
        'options': options or {}
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"API error: {response.text}")

# Usage
chordpro_content = """
{title: My Song}
{artist: Me}

[C]This is my [G]song
[Am]Hope you like [F]it
"""

pdf_data = convert_chordpro(chordpro_content)
with open('my_song.pdf', 'wb') as f:
    f.write(pdf_data)
```