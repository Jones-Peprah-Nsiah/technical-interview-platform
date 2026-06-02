# Technical Interview Platform Backend

This is the backend for the Technical Interview Platform, built with FastAPI, SQLAlchemy, and WebSockets.

## Features
- User registration and authentication (JWT)
- Room and participant management
- Question management
- Real-time communication via WebSockets

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/Jones-Peprah-Nsiah/technical-interview-platform.git
   cd technical-interview-platform/technical-interview-platform/backend
   ```
2. Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the server:
   ```sh
   uvicorn main:app --reload --port 8001
   ```

## API Documentation
- Visit [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) for interactive API docs (Swagger UI).

## WebSocket Testing
- Use `test_ws.py` to test WebSocket connections:
   ```sh
   python test_ws.py
   ```

## Project Structure
```
backend/
    auth.py
    crud.py
    database.py
    main.py
    models.py
    requirements.txt
    schemas.py
    test_ws.py
    routers/
        participants.py
        questions.py
        rooms.py
        users.py
```

## License
MIT
