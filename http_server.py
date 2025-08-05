import sys
from socket import *


class Store:
    def __init__(self):
        self.keyValue = dict()
        self.counter = dict()

    def insertValue(self, key, value):
        if key in self.counter:
            return False
        self.keyValue[key] = value
        return True

    def getValue(self, key):
        if key in self.keyValue:
            value = self.keyValue[key]
            if key in self.counter:
                self.counter[key] = self.counter[key] - 1
                if self.counter[key] == 0:
                    self.keyValue.pop(key)
                    self.counter.pop(key)
            return value
        return None

    def deleteValue(self, key):
        if key in self.keyValue:
            if key in self.counter:
                return False
            else:
                value = self.keyValue[key]
                self.keyValue.pop(key)
                return value
        return None

    def insertCounter(self, key, count):
        if key in self.keyValue:
            if key in self.counter:
                self.counter[key] += int(count)
            else:
                self.counter[key] = int(count)
            return True
        return False

    def getCounter(self, key):
        if key in self.keyValue:
            if key in self.counter:
                return str(self.counter[key])
            else:
                return "Infinity"
        return None

    def deleteCounter(self, key):
        if key in self.counter:
            counter = self.counter[key]
            self.counter.pop(key)
            return str(counter)
        return None


class HTTPServer:
    def __init__(self, port):
        self.store = Store()
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(("", port))
        self.serverSocket.listen()

    def run(self):
        while True:
            connectionSocket, clientAddr = self.serverSocket.accept()
            buffer = b""

            while True:
                endOfHeaderIdx = buffer.find(b"  ")

                connectionClosed = False
                # get more "packets" until the end of the header is found
                while endOfHeaderIdx == -1:
                    message = connectionSocket.recv(2048)
                    buffer += message
                    endOfHeaderIdx = buffer.find(b"  ")
                    connectionClosed = False

                    if len(message) == 0:
                        connectionSocket.close()
                        connectionClosed = True
                        break

                if connectionClosed:
                    break

                methodIdx = buffer.find(b" /")
                requestType = buffer[:methodIdx]
                responseMsg = b""

                if requestType.upper() == b"GET":
                    if buffer[methodIdx + 1 : methodIdx + 6] == b"/key/":
                        # key value req
                        endOfKeyIdx = buffer.find(b" ", methodIdx + 6)
                        key = buffer[methodIdx + 6 : endOfKeyIdx].decode("ascii")
                        value = self.store.getValue(key)
                        if value is None:
                            # GET failed
                            responseMsg = b"404 NotFound  "
                        else:
                            # GET successful
                            responseMsg = (
                                b"200 OK Content-Length "
                                + str(len(value)).encode("ascii")
                                + b"  "
                                + value
                            )

                    else:
                        # counter req
                        endOfKeyIdx = buffer.find(b" ", methodIdx + 10)
                        key = buffer[methodIdx + 10 : endOfKeyIdx].decode("ascii")
                        value = self.store.getCounter(key)
                        if value is None:
                            responseMsg = b"404 NotFound  "
                        else:
                            responseMsg = (
                                b"200 OK Content-Length "
                                + str(len(value)).encode("ascii")
                                + b"  "
                                + value.encode("ascii")
                            )
                    buffer = buffer[endOfHeaderIdx + 2 :]

                elif requestType.upper() == b"DELETE":
                    if buffer[methodIdx + 1 : methodIdx + 6] == b"/key/":
                        # key value req
                        endOfKeyIdx = buffer.find(b" ", methodIdx + 6)
                        key = buffer[methodIdx + 6 : endOfKeyIdx].decode("ascii")
                        value = self.store.deleteValue(key)
                        if not value:
                            responseMsg = b"405 MethodNotAllowed  "
                        elif value is None:
                            responseMsg = b"404 NotFound  "
                        else:
                            responseMsg = (
                                b"200 OK Content-Length "
                                + str(len(value)).encode("ascii")
                                + b"  "
                                + value
                            )

                    else:
                        # counter req
                        endOfKeyIdx = buffer.find(b" ", methodIdx + 10)
                        key = buffer[methodIdx + 10 : endOfKeyIdx].decode("ascii")
                        value = self.store.deleteCounter(key)
                        if value is None:
                            responseMsg = b"404 NotFound  "
                        else:
                            responseMsg = (
                                b"200 OK Content-Length "
                                + str(len(value)).encode("ascii")
                                + b"  "
                                + value.encode("ascii")
                            )
                    buffer = buffer[endOfHeaderIdx + 2 :]

                elif requestType.upper() == b"POST":
                    contentLengthIdx = (
                        buffer[: endOfHeaderIdx + 2].lower().rfind(b"content-length")
                    )
                    contentLengthEndIdx = buffer.find(b" ", contentLengthIdx + 15)
                    contentLength = int(
                        buffer[contentLengthIdx + 15 : contentLengthEndIdx]
                    )

                    while len(buffer[endOfHeaderIdx + 2 :]) < contentLength:
                        message = connectionSocket.recv(2048)
                        buffer += message

                    payload = buffer[
                        endOfHeaderIdx + 2 : endOfHeaderIdx + 2 + contentLength
                    ]
                    if buffer[methodIdx + 1 : methodIdx + 6] == b"/key/":
                        # key value req
                        endOfKeyIdx = buffer.find(b" ", methodIdx + 6)
                        key = buffer[methodIdx + 6 : endOfKeyIdx].decode("ascii")
                        if self.store.insertValue(key, payload):
                            responseMsg = b"200 OK  "
                        else:
                            responseMsg = b"405 MethodNotAllowed  "
                    else:
                        # counter req
                        endOfKeyIdx = buffer.find(b" ", methodIdx + 10)
                        key = buffer[methodIdx + 10 : endOfKeyIdx].decode("ascii")
                        if self.store.insertCounter(key, payload):
                            responseMsg = b"200 OK  "
                        else:
                            responseMsg = b"404 NotFound  "
                    buffer = buffer[endOfHeaderIdx + 2 + contentLength :]

                connectionSocket.send(responseMsg)


def main():
    serverPort = int(sys.argv[1])
    server = HTTPServer(serverPort)
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer terminated by user (Ctrl+C).")


if __name__ == "__main__":
    main()
