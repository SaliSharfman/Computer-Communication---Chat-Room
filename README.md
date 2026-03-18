# Chat Room - TCP & UDP Communication

## Overview
A chat room application implemented in Python using low-level socket programming.
Supports multiple clients communicating with a central server.

## Features
- Multi-client support using TCP
- UDP-based messaging option
- Real-time message broadcasting
- Connection handling and disconnection management

## Technologies
- Python
- TCP/UDP Sockets
- Networking Protocols

## How to Run
1. Run server:
   python server.py

2. Run client:
   python client.py

## Architecture
- Server handles multiple clients using threads/select
- TCP used for reliable messaging
- UDP used for lightweight communication

## Challenges
- Managing multiple concurrent connections
- Handling client disconnections gracefully
- Synchronizing messages between clients
