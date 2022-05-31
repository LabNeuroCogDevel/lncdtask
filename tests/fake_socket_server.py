#!/usr/bin/env python
import socket
from time import time
import os

def socket_collect(host='127.0.0.1', port=5000, verbose=False):
    messages = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if verbose:
        print(f"# waiting on {host}:{port}")
    s.bind((host, port))
    s.listen(1)
    con, addr = s.accept()
    if verbose:
        print(f"# connected to {addr}")
    while True:
        data = con.recv(1024)
        recv_time = time()
        if not data:
            if verbose:
                print("# empty data, closing")
            data = b'END'
            messages.append((recv_time,data))
            break

        if verbose:
            print(f"{recv_time:.5f} {data}\n")

        messages.append((recv_time,data))
    return messages

def write_collection(fname, m):
    """socket_collect is an array of tuples: [(timestamp, message)]
    write that to a tsv"""
    nmsg = len(m)
    if fname and nmsg > 0:
        with open(fname, 'w') as f:
            for i in range(nmsg):
                f.write(f"{m[i][0]}\t{m[i][1].decode()}\n")

if __name__ == "__main__":
    """USAGE:
      tests/socket_server.py debug/dollarreward.tsv &
      ET_HOST=localhost lncdtask/dollarreward.py

      VPLOOP=1 tests/socket_server.py
      wine ViewPointClient_64.exe
    """
    import sys
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        print(f"writting to {fname}")

    messages = socket_collect(verbose=True)
    # if we want to connect to viewpoint client
    # we need to resume after sending an empty message
    while(os.environ.get('VPLOOP')):
        messages.append(socket_collect(verbose=True))
    if fname:
        write_collection(fname, messages)
