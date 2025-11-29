"""
adv_server.py
Advanced multi-client encrypted server with:
- Threading
- Chat logging
- Friendly timestamps
- Clean JSON messages (reply + color)
- Admin commands
- Safe disconnect handling
"""

import socket
import threading
import json
import datetime
import random
import os
from typing import List, Tuple

from encryption import encrypt_text, decrypt_text


# --------------------------------
# Friendly date helper
# --------------------------------
def friendly_now() -> str:
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")


# ---------------------------
# Server Configuration
# ---------------------------

HOST = "127.0.0.1"
PORT = 5050
QUOTES_FILE = "quotes.json"
CHAT_LOG_FILE = "chat_log.txt"

clients: List[Tuple[socket.socket, Tuple[str, int]]] = []
shutdown_flag = False


# ---------------------------
# Helpers
# ---------------------------

def load_quotes():
    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return [
            "Progress, not perfection.",
            "Every expert was once a beginner.",
            "Small steps lead to big change."
        ]


quotes = load_quotes()


def log_chat(msg: str):
    with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def build_response(status, data=None, error=None):
    return json.dumps({"status": status, "data": data, "error": error})


# ---------------------------
# Client Thread
# ---------------------------

def client_thread(conn: socket.socket, addr: Tuple[str, int]):
    print(f"[SERVER] Client connected: {addr}")
    clients.append((conn, addr))

    try:
        while True:
            try:
                encrypted_data = conn.recv(4096)
            except ConnectionResetError:
                break

            if not encrypted_data:
                break

            try:
                decrypted = decrypt_text(encrypted_data.decode("utf-8"))
                req = json.loads(decrypted)
            except:
                continue

            req_type = req.get("type")

            # CHAT -----------------------------------
            if req_type == "chat":
                user = req.get("user", "Unknown")
                msg = req.get("message", "")
                color = req.get("color", "reset")

                timestamp = friendly_now()
                log_chat(f"{timestamp} - {user}: {msg}")

                resp = build_response("ok", {
                    "reply": f"{user}: {msg}",
                    "color": color
                })
                conn.sendall(encrypt_text(resp).encode("utf-8"))

            # TIME -----------------------------------
            elif req_type == "time":
                resp = build_response("ok", {"server_time": friendly_now()})
                conn.sendall(encrypt_text(resp).encode("utf-8"))

            # MATH -----------------------------------
            elif req_type == "math":
                try:
                    a = float(req.get("a", 0))
                    b = float(req.get("b", 0))
                    resp = build_response("ok", {"a": a, "b": b, "sum": a + b})
                except Exception as e:
                    resp = build_response("error", error=str(e))

                conn.sendall(encrypt_text(resp).encode("utf-8"))

            # QUOTE -----------------------------------
            elif req_type == "quote":
                resp = build_response("ok", {"quote": random.choice(quotes)})
                conn.sendall(encrypt_text(resp).encode("utf-8"))

            # HISTORY -----------------------------------
            elif req_type == "history":
                history = ""
                if os.path.exists(CHAT_LOG_FILE):
                    with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
                        history = f.read()
                resp = build_response("ok", {"history": history})
                conn.sendall(encrypt_text(resp).encode("utf-8"))

            # QUIT -----------------------------------
            elif req_type == "quit":
                resp = build_response("ok", {"message": "Goodbye!"})
                conn.sendall(encrypt_text(resp).encode("utf-8"))
                break

            else:
                resp = build_response("error", error="Unknown request type")
                conn.sendall(encrypt_text(resp).encode("utf-8"))

    finally:
        print(f"[SERVER] Client disconnected: {addr}")
        conn.close()
        for c in clients:
            if c[0] is conn:
                clients.remove(c)
                break


# ---------------------------
# Admin Commands
# ---------------------------

def admin_commands(server_socket):
    global shutdown_flag

    while True:
        cmd = input().strip().upper()

        if cmd == "LIST":
            print("\n[SERVER] Connected clients:")
            for _, a in clients:
                print(" -", a)
            print()

        elif cmd.startswith("BROADCAST "):
            msg = cmd.replace("BROADCAST ", "")
            resp = build_response("ok", {"reply": msg, "color": "yellow"})
            encrypted = encrypt_text(resp).encode("utf-8")

            for conn, _ in clients:
                try:
                    conn.sendall(encrypted)
                except:
                    pass
            print("[SERVER] Broadcast sent.\n")

        elif cmd == "SHUTDOWN":
            shutdown_flag = True
            server_socket.close()
            break


# ---------------------------
# MAIN
# ---------------------------

def start_server():
    global shutdown_flag

    print(f"[SERVER] Starting on {HOST}:{PORT}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        threading.Thread(target=admin_commands, args=(s,), daemon=True).start()

        print("[SERVER] Ready. Waiting for clients...")

        while not shutdown_flag:
            try:
                conn, addr = s.accept()
            except:
                break

            threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()

    print("[SERVER] Shut down.")


if __name__ == "__main__":
    start_server()
