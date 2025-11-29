# Networking Module Project Documentation

## Overview

I am always looking for opportunities to deepen my understanding of real-world communication systems. Networking is an essential skill for building modern distributed applications such as chat servers, IoT devices, multiplayer games, dashboards, and remote services.

This project is a fully functional networking system that demonstrates secure, structured communication between multiple programs running simultaneously on the same network. It includes:

* A multi-threaded advanced TCP server
* A terminal-based encrypted client
* A Tkinter GUI client with real-time message handling
* Automatic chat logging
* Color-coded messaging
* Friendly human-readable timestamps
* Basic encryption support for all messages
* Administrative server commands (`LIST`, `BROADCAST`, `SHUTDOWN`)
* A structured JSON-based message protocol

Users can send chat messages, view history, run math operations, retrieve motivational quotes, request the current time, and interact with multiple connected clients at once.

### How to Use

1. Start the server:

```
python adv_server.py
```

2. Start one or more clients:

```
python adv_client.py
```

Or launch the GUI version:

```
python gui_client.py
```

### Project Purpose

The purpose of building this software was to improve my knowledge and experience with:

* Multi-client server architecture
* TCP socket programming
* GUI programming in Python
* Designing encrypted message protocols
* Real-time communication between processes
* Building scalable and structured client-server systems

### Software Demonstration

A 4–5 minute video demonstrates how to start the server, run the terminal and GUI clients, show multi-client communication, use admin commands, and walk through the code.

**YouTube Demo Video:**
[*(Insert link here)*](https://youtu.be/K-qL4mHDBu8)

**GitHub Repository:**
[*(Insert link here)*](https://github.com/elorajm/NetworkingModule)

---

## Network Communication

### Architecture

This project uses a Client–Server architecture. The server listens continuously and accepts multiple simultaneous client connections using threads.

### Transport Protocol

* TCP (Transmission Control Protocol)
* Port: 5050
* Host: 127.0.0.1 (localhost)

### Message Format

All messages exchanged between client and server are JSON objects. They are encrypted using a simple XOR-based cipher and Base64 encoded.

Example Request:

```
{
  "type": "chat",
  "user": "Elora",
  "message": "Hello!",
  "color": "green"
}
```

Example Response:

```
{
  "status": "ok",
  "data": {
    "reply": "Elora: Hello!"
  },
  "error": null
}
```

---

## Development Environment

### Tools Used

* Visual Studio Code
* PowerShell
* Git & GitHub
* Tkinter for GUI

### Programming Language & Libraries

Python 3.13 with built-in libraries:

* socket
* threading
* json
* datetime
* tkinter
* base64
* random
* os

---

## Useful Websites

* [https://docs.python.org/3/library/socket.html](https://docs.python.org/3/library/socket.html)
* [https://docs.python.org/3/library/threading.html](https://docs.python.org/3/library/threading.html)
* [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
* [https://realpython.com/python-sockets/](https://realpython.com/python-sockets/)
* [https://en.wikipedia.org/wiki/OSI_model](https://en.wikipedia.org/wiki/OSI_model)
* [https://www.json.org/json-en.html](https://www.json.org/json-en.html)
* [https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

---

## Future Work

* Add public/private key encryption
* Implement file transfers
* Add user authentication
* Improve GUI with themes and message bubbles
* Support private messaging
* Add peer-to-peer communication mode
* Package server and clients as standalone executables
