# run.py
from src.api.main import app

if __name__ == '__main__':
    """
    Main entry point to run the Flask web application.
    
    - `host='0.0.0.0'` makes the server accessible on your local network.
    - `port=5001` sets the port (you can change this).
    - `debug=True` enables auto-reloading when you change the code.
    """
    print("Starting SYDE Course Planner API server...")
    print("Access it at http://127.0.0.1:5001 or your local IP.")
    app.run(host='0.0.0.0', port=5001, debug=True)