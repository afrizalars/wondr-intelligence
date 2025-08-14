#!/usr/bin/env python
"""
Simple server runner that works around asyncio issues
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("Starting server on http://localhost:8001")
    print("API docs: http://localhost:8001/api/docs")
    print("Press Ctrl+C to stop")
    
    # Run without reload to avoid watchfiles issues
    uvicorn.run(
        app,
        host="127.0.0.1",  # Use 127.0.0.1 instead of 0.0.0.0
        port=8001,
        log_level="info",
        access_log=True,
        loop="asyncio"  # Explicitly specify asyncio loop
    )