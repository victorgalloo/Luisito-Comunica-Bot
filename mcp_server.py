"""
Simple MCP Server for YouTube Transcripts
Provides HTTP API endpoint compatible with our transcriber
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    logger.warning("youtube-transcript-api not available")
    TRANSCRIPT_API_AVAILABLE = False


class TranscriptHandler(BaseHTTPRequestHandler):
    """Handle transcript requests"""
    
    def do_POST(self):
        """Handle POST requests to /api/transcript"""
        if self.path == '/api/transcript':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                video_url = data.get('url', '')
                
                logger.info(f"Transcribing video: {video_url}")
                
                # Extract video ID from URL
                video_id = self._extract_video_id(video_url)
                
                if not video_id:
                    self._send_error(400, "Invalid YouTube URL")
                    return
                
                # Get transcript
                transcript = self._get_transcript(video_id)
                
                if transcript:
                    self._send_json(200, transcript)
                else:
                    self._send_error(500, "Failed to get transcript")
                    
            except Exception as e:
                logger.error(f"Error: {e}")
                self._send_error(500, str(e))
        else:
            self._send_error(404, "Not Found")
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self._send_json(200, {'status': 'healthy'})
        elif self.path == '/':
            self._send_json(200, {
                'service': 'YouTube Transcript MCP Server',
                'status': 'running',
                'api_endpoint': '/api/transcript'
            })
        else:
            self._send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def _extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        try:
            parsed = urlparse(url)
            if parsed.hostname in ['youtu.be']:
                return parsed.path[1:]
            elif 'youtube.com' in parsed.hostname:
                query = parse_qs(parsed.query)
                return query.get('v', [None])[0]
        except:
            pass
        return None
    
    def _get_transcript(self, video_id):
        """Get transcript for video ID"""
        if not TRANSCRIPT_API_AVAILABLE:
            return None
        
        try:
            # Create API instance
            api = YouTubeTranscriptApi()
            
            # Get transcript list
            transcript_list = api.list(video_id)
            
            # Try to find Spanish or English transcript
            try:
                transcript = transcript_list.find_transcript(['es', 'en'])
            except:
                # Try auto-generated
                transcript = transcript_list.find_generated_transcript(['es', 'en'])
            
            # Translate to Spanish if needed
            if transcript.language_code != 'es':
                transcript = transcript.translate('es')
            
            # Fetch transcript data
            transcript_data = transcript.fetch()
            
            # Extract text (handle new API format)
            # transcript_data is a FetchedTranscript (iterable of FetchedTranscriptSnippet)
            text = ' '.join([item.text for item in transcript_data])
            transcript_data = [{'text': item.text, 'start': item.start, 'duration': item.duration} for item in transcript_data]
            
            return {
                'text': text,
                'segments': transcript_data,
                'language': 'es',
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Failed to get transcript: {e}")
            return None
    
    def _send_json(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        self._send_json(status_code, {'error': message})


def run_server(port=8080):
    """Run the MCP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TranscriptHandler)
    logger.info(f"Starting MCP YouTube Transcript Server on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        httpd.shutdown()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    run_server(port)

