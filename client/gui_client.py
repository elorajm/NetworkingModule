"""
gui_client.py
Fully updated GUI client with REAL Tkinter color tags.
Supports:
- Chat with color
- Time
- Math
- Quotes
- History
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import socket
import threading
import json
import time
import re

from encryption import encrypt_text, decrypt_text

HOST = "127.0.0.1"
PORT = 5050


# ---------------------------
# Strip ANSI escape codes
# ---------------------------
def strip_ansi(text: str) -> str:
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)


# ---------------------------
# GUI Client Class
# ---------------------------
class GUIClient:
    def __init__(self, root):
        self.root = root
        self.sock = None
        self.username = ""

        root.title("Networking GUI Client")
        root.geometry("700x600")

        # ---------------------------
        # TOP FRAME
        # ---------------------------
        top = ttk.Frame(root)
        top.pack(pady=5)

        ttk.Label(top, text="Username: ").pack(side=tk.LEFT)
        self.u_entry = ttk.Entry(top, width=20)
        self.u_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(top, text="Connect", command=self.connect).pack(side=tk.LEFT, padx=10)

        # ---------------------------
        # OUTPUT WINDOW
        # ---------------------------
        self.output = scrolledtext.ScrolledText(root, width=80, height=20)
        self.output.pack(pady=10)

        # Define color tags
        self.output.tag_config("red", foreground="red")
        self.output.tag_config("green", foreground="green")
        self.output.tag_config("blue", foreground="blue")
        self.output.tag_config("yellow", foreground="gold")
        self.output.tag_config("purple", foreground="purple")
        self.output.tag_config("cyan", foreground="cyan")
        self.output.tag_config("reset", foreground="black")

        # ---------------------------
        # CHAT INPUT
        # ---------------------------
        chat = ttk.Frame(root)
        chat.pack()

        ttk.Label(chat, text="Message: ").pack(side=tk.LEFT)
        self.msg_entry = ttk.Entry(chat, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(chat, text="Color: ").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="reset")
        ttk.Combobox(
            chat,
            textvariable=self.color_var,
            values=["reset", "red", "green", "blue", "yellow", "purple", "cyan"],
            width=7
        ).pack(side=tk.LEFT)

        # ---------------------------
        # BUTTON ROW
        # ---------------------------
        buttons = ttk.Frame(root)
        buttons.pack(pady=10)

        ttk.Button(buttons, text="Send", command=self.send_chat).grid(row=0, column=0)
        ttk.Button(buttons, text="Time", command=self.get_time).grid(row=0, column=1)
        ttk.Button(buttons, text="Math", command=self.do_math).grid(row=0, column=2)
        ttk.Button(buttons, text="Quote", command=self.get_quote).grid(row=0, column=3)
        ttk.Button(buttons, text="History", command=self.get_history).grid(row=0, column=4)
        ttk.Button(buttons, text="Quit", command=self.quit).grid(row=0, column=5)

    # ---------------------------
    # Write to output with color
    # ---------------------------
    def write_out(self, text, color="reset"):
        clean = strip_ansi(text)
        self.output.insert(tk.END, clean, color)
        self.output.see(tk.END)

    # ---------------------------
    # CONNECT
    # ---------------------------
    def connect(self):
        if self.sock:
            return

        name = self.u_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter username first.")
            return

        self.username = name

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.sock.setblocking(False)

            self.write_out("Connected to server.\n", "cyan")

            threading.Thread(target=self.listen, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.sock = None

    # ---------------------------
    # LISTENER
    # ---------------------------
    def listen(self):
        while True:
            if not self.sock:
                break

            try:
                data = self.sock.recv(4096)
                if not data:
                    break

                dec = decrypt_text(data.decode("utf-8"))
                resp = json.loads(dec)
                self.handle_response(resp)

            except BlockingIOError:
                pass
            except ConnectionResetError:
                self.write_out("Disconnected.\n", "red")
                break
            except:
                pass

            time.sleep(0.05)

    # ---------------------------
    # RESPONSE HANDLER
    # ---------------------------
    def handle_response(self, resp):
        data = resp.get("data", {})
        color = data.get("color", "reset")

        # CHAT
        if "reply" in data:
            self.write_out(data["reply"] + "\n", color)

        # TIME
        elif "server_time" in data:
            self.write_out("Server Time: " + data["server_time"] + "\n", "cyan")

        # QUOTE
        elif "quote" in data:
            self.write_out("Quote: " + data["quote"] + "\n", "purple")

        # MATH
        elif "sum" in data:
            a = data["a"]
            b = data["b"]
            s = data["sum"]
            self.write_out(f"Math Result: {a} + {b} = {s}\n", "blue")

        # HISTORY
        elif "history" in data:
            self.write_out("\n--- Chat History ---\n", "yellow")
            self.write_out(data["history"] + "\n", "reset")
            self.write_out("--------------------\n", "yellow")

    # ---------------------------
    # SEND REQUEST HELPER
    # ---------------------------
    def send_req(self, req):
        if not self.sock:
            return None

        msg = json.dumps(req)
        self.sock.sendall(encrypt_text(msg).encode("utf-8"))

        for _ in range(20):
            try:
                data = self.sock.recv(4096)
                dec = decrypt_text(data.decode("utf-8"))
                return json.loads(dec)
            except:
                time.sleep(0.05)
        return None

    # ---------------------------
    # BUTTON ACTIONS
    # ---------------------------
    def send_chat(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        color = self.color_var.get()
        resp = self.send_req({
            "type": "chat",
            "user": self.username,
            "message": msg,
            "color": color
        })

        if resp:
            self.handle_response(resp)

        self.msg_entry.delete(0, tk.END)

    def get_time(self):
        resp = self.send_req({"type": "time"})
        if resp:
            self.handle_response(resp)

    def do_math(self):
        try:
            a = float(simpledialog.askstring("Math", "Enter first number:"))
            b = float(simpledialog.askstring("Math", "Enter second number:"))
        except:
            self.write_out("Invalid input.\n", "red")
            return

        resp = self.send_req({"type": "math", "a": a, "b": b})
        if resp:
            self.handle_response(resp)

    def get_quote(self):
        resp = self.send_req({"type": "quote"})
        if resp:
            self.handle_response(resp)

    def get_history(self):
        resp = self.send_req({"type": "history"})
        if resp:
            self.handle_response(resp)

    def quit(self):
        self.send_req({"type": "quit"})
        self.write_out("Disconnected.\n", "red")
        self.root.destroy()


# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    GUIClient(root)
    root.mainloop()
