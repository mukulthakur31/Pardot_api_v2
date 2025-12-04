#!/usr/bin/env python3
"""
Pardot API Server Startup Script
Provides better error handling and graceful shutdown
"""

import os
import sys
import signal
import threading
import time
from app import create_app

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print('\n🛑 Received shutdown signal. Cleaning up...')
    
    # Give threads time to finish
    print('⏳ Waiting for active threads to complete...')
    time.sleep(2)
    
    print('✅ Server shutdown complete.')
    sys.exit(0)

def main():
    """Main server startup function"""
    try:
        print('🚀 Starting Pardot API Server...')
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create Flask app
        app = create_app()
        
        # Configure server settings
        host = '127.0.0.1'
        port = 4001
        debug = True
        
        print(f'🌐 Server starting on http://{host}:{port}')
        print('📊 Pardot Analytics Platform Ready')
        print('⚠️  Press Ctrl+C to stop the server')
        
        # Start the server with better error handling
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False  # Disable reloader to prevent threading issues
        )
        
    except KeyboardInterrupt:
        print('\n🛑 Server stopped by user.')
    except Exception as e:
        print(f'❌ Server startup failed: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()