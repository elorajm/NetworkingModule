"""
adv_client.py
Advanced encrypted client:
- Color output
- Friendly timestamps
- Full menu
"""

import socket
import json
import os

# Enable ANSI color codes on Windows
os.system("")

from encryption import encrypt_text, decrypt_text

HOST = "127.0.0.1"
PORT = 5050

COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "reset": "\033[0m"
}


def send_request(sock, req):
    msg = json.dumps(req)
    encrypted = encrypt_text(msg)
    sock.sendall(encrypted.encode("utf-8"))

    encrypted_in = sock.recv(4096)
    decrypted = decrypt_text(encrypted_in.decode("utf-8"))
    return json.loads(decrypted)


def print_response(resp):
    data = resp.get("data", {})
    reply = data.get("reply")
    color = data.get("color", "reset")

    if reply:
        print(f"{COLORS.get(color, COLORS['reset'])}{reply}{COLORS['reset']}")
    else:
        print(json.dumps(resp, indent=4))


def run_client():
    print("=== Advanced Client ===")
    username = input("Enter username: ").strip() or "User"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Connecting...")
        s.connect((HOST, PORT))
        print("Connected!\n")

        while True:
            print("1. Chat")
            print("2. Get Time")
            print("3. Add Numbers")
            print("4. Get Quote")
            print("5. View History")
            print("6. Quit")

            choice = input("Choose: ")

            if choice == "1":
                msg = input("Message: ")
                color = input("Color (red/green/blue/yellow/purple/cyan/reset): ")
                resp = send_request(s, {
                    "type": "chat",
                    "user": username,
                    "message": msg,
                    "color": color
                })
                print_response(resp)

            elif choice == "2":
                resp = send_request(s, {"type": "time"})
                print_response(resp)

            elif choice == "3":
                a = float(input("a: "))
                b = float(input("b: "))
                resp = send_request(s, {"type": "math", "a": a, "b": b})
                print_response(resp)

            elif choice == "4":
                resp = send_request(s, {"type": "quote"})
                print_response(resp)

            elif choice == "5":
                resp = send_request(s, {"type": "history"})
                print(resp["data"]["history"])

            elif choice == "6":
                send_request(s, {"type": "quit"})
                print("Goodbye!")
                break


if __name__ == "__main__":
    run_client()
