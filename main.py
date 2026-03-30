import uvicorn
import socket
import os

def check_port(port=8081):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

if __name__ == "__main__":
    if not check_port(8081):
        print("Port 8081 is already in use. Please check if another instance is running.")
        exit(1)
        
    print("="*60)
    print("🚀 DeepCV-Analyzer")
    print("✅ System starting up...")
    print("🌐 Frontend & Backend unified on: http://localhost:8081")
    print("="*60)
    
    # Run the single fastAPI server that mounts the frontend
    uvicorn.run("api_server:app", host="0.0.0.0", port=8081, reload=True)