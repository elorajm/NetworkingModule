"""
client.py

This file contains the client-side code for communicating with the server
over a TCP connection. The client sends JSON requests to the server and
displays the JSON responses.

This client supports the following request types:
- chat   : send a text message to the server
- time   : ask the server for the current time
- math   : send two numbers, receive the sum
- quote  : request a random motivational quote
- quit   : close the connection gracefully

This file is heavily commented for clarity and to meet the documentation
requirements of the Networking module.
"""

import socket      # For network connections
import json        # For encoding/decoding messages
from typing import Dict, Any


# ---------------------------
# Configuration constants
# ---------------------------

# Must match the server's host and port
HOST = "127.0.0.1"
PORT = 5000


# ---------------------------
# Helper Functions
# ---------------------------

def send_request(sock: socket.socket, request_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a dictionary as a JSON message to the server and wait for a response.

    The server expects JSON strings, so we convert our dictionary into
    a string using json.dumps(), and then encode it into bytes.
    """
    # Convert Python dict → JSON string
    request_str = json.dumps(request_obj) + "\n"

    # Encode to bytes and send
    sock.sendall(request_str.encode("utf-8"))

    # Receive server response (up to 1024 bytes)
    data = sock.recv(1024)

    # Decode bytes → string, then parse JSON
    response = json.loads(data.decode("utf-8").strip())
    return response


def print_response(response: Dict[str, Any]) -> None:
    """
    Nicely print the server response.
    """
    print("\n--- Server Response ---")
    print(json.dumps(response, indent=4))
    print("-----------------------\n")


# ---------------------------
# Main Client Program
# ---------------------------

def run_client() -> None:
    """
    Connect to the server and allow the user to perform different actions.
    """
    print("Connecting to server...")

    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to the server
        sock.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        # Main menu loop
        while True:
            print("\nChoose a request type:")
            print("1. Chat message")
            print("2. Get server time")
            print("3. Add two numbers (math)")
            print("4. Get a random quote")
            print("5. Quit")

            choice = input("\nEnter option (1-5): ").strip()

            # -------------------------
            # Chat request
            # -------------------------
            if choice == "1":
                message = input("Enter a chat message: ")
                request = {
                    "type": "chat",
                    "message": message
                }
                response = send_request(sock, request)
                print_response(response)

            # -------------------------
            # Time request
            # -------------------------
            elif choice == "2":
                request = {"type": "time"}
                response = send_request(sock, request)
                print_response(response)

            # -------------------------
            # Math request
            # -------------------------
            elif choice == "3":
                try:
                    a = float(input("Enter first number: "))
                    b = float(input("Enter second number: "))
                except ValueError:
                    print("Invalid number. Try again.")
                    continue

                request = {
                    "type": "math",
                    "a": a,
                    "b": b
                }
                response = send_request(sock, request)
                print_response(response)

            # -------------------------
            # Quote request
            # -------------------------
            elif choice == "4":
                request = {"type": "quote"}
                response = send_request(sock, request)
                print_response(response)

            # -------------------------
            # Quit
            # -------------------------
            elif choice == "5":
                request = {"type": "quit"}
                response = send_request(sock, request)
                print_response(response)
                print("Closing connection...")
                break

            else:
                print("Invalid choice. Please select 1–5.")

    print("Client has closed.")
    

# ---------------------------
# Entry point
# ---------------------------

if __name__ == "__main__":
    run_client()
