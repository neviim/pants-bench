"""
A fake HTTP server using Tornado.

This code is based on a snippet posted by Nicholas Piël on his blog at:
http://nichol.as/asynchronous-servers-in-python

For each \r\n\r\n-delimited string it receives, this server will send a
very short HTTP response. Useful for using HTTP benchmarking tools to
measure a framework's performance without involving the HTTP stack.
"""

import errno
import functools
import socket

from tornado import ioloop, iostream

def on_read(stream, data):
    read_done = functools.partial(on_read, stream)
    write_done = functools.partial(stream.read_until, '\r\n\r\n', read_done)
    stream.write("HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!\r\n", write_done)

def on_accept(sock, fd, events):
    while True:
        try:
            connection, address = sock.accept()
        except socket.error, e:
            if e[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        connection.setblocking(0)
        stream = iostream.IOStream(connection)
        stream.read_until('\r\n\r\n', functools.partial(do_response, stream))

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(("", 8080))
    sock.listen(1024)
    io_loop = ioloop.IOLoop.instance()
    callback = functools.partial(on_accept, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
