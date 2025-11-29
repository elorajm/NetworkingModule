"""
server.py

This file contains the server-side code for a simple TCP networking project.
The server listens on a port, accepts client connections, and responds to
different kinds of requests sent as JSON strings.

Features this server supports:
- "chat"  : Echoes back a message with a server timestamp.
- "time"  : Returns the current server time as a string.
- "math"  : Adds two numbers and returns the result.
- "quote" : Returns a random quote from a local quotes.json file.

This file is heavily commented so that another student (or my future self)
can follow along and understand how basic networking with Python sockets works.
"""

import socket      # Built-in Python library for networking
import json        # For encoding/decoding JSON messages
import datetime    # For timestamps and time responses
import random      # For choosing a random quote
from typing import Dict, Any, Optional, List


# ---------------------------
# Configuration constants
# ---------------------------

# This is the IP address the server will listen on.
# 127.0.0.1 means "localhost", which is this same computer.
HOST = "127.0.0.1"

# This is the port number the server will listen on.
# Ports are like "doors" into the computer for network traffic.
PORT = 5000

# This is the name of the JSON file that will store quotes
QUOTES_FILE = "quotes.json"


# ---------------------------
# Helper functions
# ---------------------------

def load_quotes(file_path: str) -> List[str]:
    """
    Load a list of quotes from a JSON file.

    The JSON file should contain something like:
        ["Quote 1", "Quote 2", "Quote 3"]

    If there is any problem reading the file, we fall back to a small
    built-in list so the server still works.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # We expect a list of strings. If not, raise an error.
        if not isinstance(data, list):
            raise ValueError("quotes.json does not contain a list")

        return [str(q) for q in data]  # make sure everything is a string

    except Exception as e:
        print(f"[SERVER] Could not load quotes from {file_path}: {e}")
        print("[SERVER] Falling back to default quotes.")
        # Fallback quotes if file is missing or invalid
        return [
            "Learning to code is like learning a superpower.",
            "Small steps every day lead to big progress.",
            "Failure is data. Use it to adjust and try again."
        ]


def build_response(status: str, data: Any = None, error: Optional[str] = None) -> str:
    """
    Build a JSON response string that the server will send to the client.

    status: "ok" or "error"
    data  : the useful result we want to send back
    error : an error message if something went wrong

    We return a JSON string terminated with a newline (\n) so the client
    knows where one message ends.
    """
    response_obj: Dict[str, Any] = {
        "status": status,
        "data": data,
        "error": error
    }
    # Convert Python dictionary to JSON string
    return json.dumps(response_obj) + "\n"


def handle_request(request: Dict[str, Any], quotes: List[str]) -> str:
    """
    Take a parsed JSON request from the client and return a JSON response string.

    The request is expected to have a "type" field that tells us
    what the client wants the server to do.
    """
    req_type = request.get("type")

    # 1. Chat request
    if req_type == "chat":
        message = request.get("message", "")
        # Add a timestamp for fun and for learning
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reply = f"Server received your message at {now}: {message}"
        return build_response(status="ok", data={"reply": reply})

    # 2. Time request
    if req_type == "time":
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return build_response(status="ok", data={"server_time": now})

    # 3. Math request
    if req_type == "math":
        # We expect the client to send numbers a and b
        try:
            a = float(request.get("a", 0))
            b = float(request.get("b", 0))
            result = a + b
            return build_response(status="ok", data={"a": a, "b": b, "sum": result})
        except Exception as e:
            return build_response(status="error", data=None, error=str(e))

    # 4. Quote request
    if req_type == "quote":
        if not quotes:
            return build_response(status="error", data=None, error="No quotes available.")
        quote = random.choice(quotes)
        return build_response(status="ok", data={"quote": quote})

    # 5. Quit request (tells the server to close this client connection)
    if req_type == "quit":
        # The server will handle this specially in the connection loop.
        return build_response(status="ok", data={"message": "Connection closing."})

    # If we reach this point, the request type is unknown
    return build_response(status="error", data=None, error=f"Unknown request type: {req_type}")


# ---------------------------
# Main server loop
# ---------------------------

def run_server() -> None:
    """
    Main function that starts the server, listens for one client at a time,
    and handles requests in a loop.

    For simplicity, this server handles one client connection at a time.
    That is enough to demonstrate the networking concepts required
    for this course module.
    """

    # Load quotes once at startup
    quotes = load_quotes(QUOTES_FILE)

    # Create a TCP/IP socket
    # AF_INET means IPv4, SOCK_STREAM means TCP (reliable stream)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Allow the address to be reused quickly after the program closes
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to our host and port so we can listen there
        server_socket.bind((HOST, PORT))
        print(f"[SERVER] Starting server on {HOST}:{PORT} ...")

        # Start listening for incoming connections
        server_socket.listen()
        print("[SERVER] Waiting for a client to connect...")

        while True:
            # Accept a new client connection (this is a blocking call)
            client_socket, client_address = server_socket.accept()
            print(f"[SERVER] Client connected from {client_address}")

            # Use "with" so the client socket is automatically closed
            with client_socket:
                # For this project, we will allow multiple requests
                # from the same client until they send a "quit" request.
                while True:
                    # Receive up to 1024 bytes from the client
                    data = client_socket.recv(1024)

                    # If no data is received, the client disconnected
                    if not data:
                        print("[SERVER] Client disconnected.")
                        break

                    # Decode bytes to string
                    message_str = data.decode("utf-8").strip()
                    print(f"[SERVER] Raw message from client: {message_str}")

                    try:
                        # Parse the JSON string into a Python dictionary
                        request_obj = json.loads(message_str)
                    except json.JSONDecodeError as e:
                        # If parsing fails, send back an error response
                        error_response = build_response(
                            status="error",
                            data=None,
                            error=f"Invalid JSON: {e}"
                        )
                        client_socket.sendall(error_response.encode("utf-8"))
                        continue

                    # Build a response based on the request
                    response_str = handle_request(request_obj, quotes)

                    # Send the response back to the client
                    client_socket.sendall(response_str.encode("utf-8"))

                    # If this was a quit request, close the connection
                    if request_obj.get("type") == "quit":
                        print("[SERVER] Client requested to close the connection.")
                        break

            # After client disconnects or requests quit, go back to waiting
            print("[SERVER] Waiting for a new client to connect...")


# ---------------------------
# Entry point
# ---------------------------

if __name__ == "__main__":
    # When we run `python server.py`, this code will execute.
    # When we import server.py from somewhere else, this part will NOT run,
    # which is a nice Python feature.
    run_server()
