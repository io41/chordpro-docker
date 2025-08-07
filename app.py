#!/usr/bin/env python3

import os
import tempfile
import subprocess
import json
import logging
import sys
import hmac
import hashlib
from pathlib import Path
from functools import wraps
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Remove server header for security
    response.headers.pop('Server', None)
    return response

# Authentication configuration
VALID_API_KEYS = set()
DEVELOPMENT_MODE = False

def secure_compare_api_key(provided_key, valid_key):
    """Securely compare API keys using constant-time comparison to prevent timing attacks."""
    if not isinstance(provided_key, str) or not isinstance(valid_key, str):
        return False
    
    # Convert to bytes for HMAC comparison
    provided_bytes = provided_key.encode('utf-8')
    valid_bytes = valid_key.encode('utf-8')
    
    # Use HMAC for constant-time comparison
    return hmac.compare_digest(provided_bytes, valid_bytes)

def is_valid_api_key(provided_key):
    """Check if provided API key is valid using secure comparison."""
    if not provided_key:
        return False
    
    # Compare against all valid keys using secure comparison
    for valid_key in VALID_API_KEYS:
        if secure_compare_api_key(provided_key, valid_key):
            return True
    
    return False

def load_api_keys():
    """Load API keys from environment variables."""
    global VALID_API_KEYS, DEVELOPMENT_MODE
    
    # Check for explicit development mode
    DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', '').lower() in ('true', '1', 'yes', 'on')
    
    # Load from comma-separated environment variable
    api_keys_env = os.getenv('API_KEYS', '')
    if api_keys_env:
        keys = [key.strip() for key in api_keys_env.split(',') if key.strip()]
        VALID_API_KEYS.update(keys)
        logger.info(f"Loaded {len(keys)} API keys from API_KEYS environment variable")
    
    # Load from individual environment variables (API_KEY_1, API_KEY_2, etc.)
    individual_keys = 0
    for key, value in os.environ.items():
        if key.startswith('API_KEY_') and value:
            VALID_API_KEYS.add(value.strip())
            individual_keys += 1
    
    if individual_keys > 0:
        logger.info(f"Loaded {individual_keys} additional API keys from individual environment variables")
    
    # Security: Validate API key strength
    weak_keys = [key for key in VALID_API_KEYS if len(key) < 16]
    if weak_keys:
        logger.warning(f"Found {len(weak_keys)} API keys shorter than 16 characters - consider using stronger keys")
    
    # Production security: Require API keys unless explicitly in development mode
    if not VALID_API_KEYS and not DEVELOPMENT_MODE:
        logger.error("SECURITY: No API keys configured and not in development mode.")
        logger.error("Either set API_KEYS environment variable or set DEVELOPMENT_MODE=true")
        logger.error("Refusing to start without authentication in production mode.")
        sys.exit(1)
    
    if DEVELOPMENT_MODE:
        logger.warning("DEVELOPMENT MODE ENABLED - Authentication disabled!")
        logger.warning("Do not use DEVELOPMENT_MODE=true in production!")
        if VALID_API_KEYS:
            logger.warning("API keys configured but ignored in development mode")
    elif VALID_API_KEYS:
        logger.info(f"Production mode: Authentication enabled with {len(VALID_API_KEYS)} API key(s)")

def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth for health check and index page
        if request.endpoint in ['health', 'index']:
            return f(*args, **kwargs)
        
        # In development mode, skip authentication
        if DEVELOPMENT_MODE:
            return f(*args, **kwargs)
        
        # Production mode: require valid API key
        api_key = request.headers.get('X-API-Key')
        if not api_key or not is_valid_api_key(api_key):
            logger.warning(f"Unauthorized access attempt from {request.remote_addr} to {request.endpoint}")
            raise Unauthorized("Valid API key required. Include 'X-API-Key' header.")
        
        return f(*args, **kwargs)
    return decorated_function

# Load API keys on startup
load_api_keys()

class ChordProProcessor:
    """Handles ChordPro CLI operations with extensible configuration."""
    
    def __init__(self):
        self.supported_outputs = ['pdf', 'text', 'cho', 'html']
        self.base_cmd = ['chordpro']
    
    def process(self, content, output_format='pdf', options=None):
        """
        Process ChordPro content with specified options.
        
        Args:
            content (str): ChordPro content
            output_format (str): Output format (pdf, text, cho, html)
            options (dict): Additional CLI options
        
        Returns:
            tuple: (output_path, content_type)
        """
        if output_format not in self.supported_outputs:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        options = options or {}
        
        # Create temporary files
        input_id = str(uuid.uuid4())
        input_path = f"/tmp/input_{input_id}.cho"
        output_path = f"/tmp/output_{input_id}.{output_format}"
        
        try:
            logger.info(f"Processing ChordPro content: format={output_format}, options={options}")
            
            # Write input content
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Build command
            cmd = self.base_cmd.copy()
            cmd.extend([input_path, '-o', output_path])
            
            # Add CLI options
            self._add_options(cmd, options)
            
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            # Execute chordpro with timeout for security
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30  # 30 second timeout to prevent hanging
            )
            
            if not os.path.exists(output_path):
                logger.error(f"ChordPro command succeeded but output file not found: {output_path}")
                raise RuntimeError("ChordPro did not generate output file")
            
            file_size = os.path.getsize(output_path)
            logger.info(f"ChordPro processing completed successfully: {file_size} bytes generated")
            
            return output_path, self._get_content_type(output_format)
            
        except subprocess.TimeoutExpired:
            logger.error(f"ChordPro processing timed out after 30 seconds")
            raise RuntimeError("ChordPro processing timed out")
        except subprocess.CalledProcessError as e:
            logger.error(f"ChordPro processing failed with return code {e.returncode}: {e.stderr}")
            # Sanitize error message for security (don't expose file paths)
            error_msg = e.stderr.strip() if e.stderr else "Unknown ChordPro error"
            if input_path in error_msg:
                error_msg = error_msg.replace(input_path, "<input>")
            raise RuntimeError(f"ChordPro processing failed: {error_msg}")
        except Exception as e:
            logger.error(f"Unexpected error during ChordPro processing: {str(e)}")
            raise RuntimeError(f"Processing failed: {str(e)}")
        finally:
            # Cleanup input file
            if os.path.exists(input_path):
                try:
                    os.unlink(input_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup input file {input_path}: {e}")
    
    def _add_options(self, cmd, options):
        """Add CLI options to command."""
        # Transpose
        if 'transpose' in options:
            cmd.extend(['--transpose', str(options['transpose'])])
        
        # Metadata
        if 'meta' in options:
            for key, value in options['meta'].items():
                cmd.extend(['--meta', f"{key}={value}"])
        
        # Configuration files
        if 'config' in options:
            config_value = options['config']
            if isinstance(config_value, str):
                # Handle comma-separated configs like "ukulele,modern3"
                configs = [c.strip() for c in config_value.split(',')]
                for config in configs:
                    cmd.extend(['--config', config])
            elif isinstance(config_value, list):
                # Handle list of configs
                for config in config_value:
                    cmd.extend(['--config', config])
            else:
                # Single config (should be string but handle gracefully)
                cmd.extend(['--config', str(config_value)])
        
        # Diagrams
        if 'diagrams' in options:
            if options['diagrams']:
                cmd.append('--diagrams')
            else:
                cmd.append('--no-diagrams')
    
    def _get_content_type(self, output_format):
        """Get MIME content type for output format."""
        types = {
            'pdf': 'application/pdf',
            'text': 'text/plain',
            'cho': 'text/plain',
            'html': 'text/html'
        }
        return types.get(output_format, 'application/octet-stream')

processor = ChordProProcessor()

@app.route('/', methods=['GET'])
def index():
    """API documentation index page."""
    try:
        # Get ChordPro version
        result = subprocess.run(['chordpro', '--version'], capture_output=True, text=True)
        chordpro_version = result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        chordpro_version = "unknown"
    
    return render_template('index.html', chordpro_version=chordpro_version)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint with basic service verification."""
    status = {
        "status": "healthy", 
        "service": "chordpro-api",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    
    # Basic ChordPro availability check
    try:
        result = subprocess.run(['chordpro', '--version'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            status["chordpro_available"] = True
        else:
            status["chordpro_available"] = False
            status["status"] = "degraded"
    except Exception:
        status["chordpro_available"] = False
        status["status"] = "degraded"
    
    return jsonify(status)

@app.route('/convert', methods=['POST'])
@require_api_key
def convert():
    """
    Convert ChordPro content to specified format.
    
    Request body:
    {
        "content": "ChordPro content string",
        "output_format": "pdf|text|cho|html",
        "options": {
            "transpose": 2,
            "meta": {"title": "Song Title", "artist": "Artist Name"},
            "diagrams": true
        }
    }
    """
    output_path = None
    try:
        logger.info(f"Convert request from {request.remote_addr}")
        
        data = request.get_json()
        if not data:
            raise BadRequest("JSON body required")
        
        content = data.get('content')
        if not content:
            raise BadRequest("'content' field is required")
        
        # Input validation for security
        if not isinstance(content, str):
            raise BadRequest("'content' must be a string")
        
        if len(content) > 1024 * 1024:  # 1MB limit
            raise BadRequest("Content too large (max 1MB)")
        
        output_format = data.get('output_format', 'pdf')
        if not isinstance(output_format, str):
            raise BadRequest("'output_format' must be a string")
        
        options = data.get('options', {})
        if not isinstance(options, dict):
            raise BadRequest("'options' must be an object")
        
        # Validate options structure
        for key, value in options.items():
            if key == 'transpose' and not isinstance(value, int):
                raise BadRequest("'transpose' option must be an integer")
            elif key == 'meta' and not isinstance(value, dict):
                raise BadRequest("'meta' option must be an object")
            elif key == 'diagrams' and not isinstance(value, bool):
                raise BadRequest("'diagrams' option must be a boolean")
            elif key == 'config' and not isinstance(value, (str, list)):
                raise BadRequest("'config' option must be a string or array")
        
        # Process the content
        output_path, content_type = processor.process(content, output_format, options)
        
        # Return the file
        response = send_file(
            output_path,
            mimetype=content_type,
            as_attachment=True,
            download_name=f"output.{output_format}",
            conditional=False
        )
        
        logger.info(f"Convert request completed successfully: {output_format} format")
        return response
        
    except BadRequest as e:
        logger.warning(f"Bad request from {request.remote_addr}: {str(e)}")
        raise
    except RuntimeError as e:
        logger.error(f"Processing error for {request.remote_addr}: {str(e)}")
        raise InternalServerError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing request from {request.remote_addr}: {str(e)}")
        raise InternalServerError("Processing failed")
    finally:
        # Cleanup output file if it exists
        if output_path and os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup output file {output_path}: {e}")

@app.route('/formats', methods=['GET'])
@require_api_key
def get_formats():
    """Get supported output formats."""
    return jsonify({
        "supported_formats": processor.supported_outputs,
        "default_format": "pdf"
    })

@app.route('/options', methods=['GET'])
@require_api_key
def get_options():
    """Get supported CLI options for future expansion."""
    return jsonify({
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
                "type": "string|array",
                "description": "ChordPro configuration(s). Supports single config, comma-separated list (e.g., 'ukulele,modern3'), or array of configs",
                "examples": ["ukulele", "ukulele,modern3", ["ukulele", "modern3"]]
            }
        }
    })

if __name__ == '__main__':
    logger.info("Starting ChordPro Web API")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Flask version: {getattr(app, '__version__', 'unknown')}")
    
    # Check ChordPro installation
    try:
        result = subprocess.run(['chordpro', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info(f"ChordPro version: {result.stdout.strip()}")
        else:
            logger.error("ChordPro not properly installed or accessible")
    except Exception as e:
        logger.error(f"Failed to check ChordPro version: {e}")
    
    logger.info("Server starting on http://0.0.0.0:8080")
    logger.info("Ready to accept requests")
    
    app.run(host='0.0.0.0', port=8080, debug=False)