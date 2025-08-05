import socket
import sys


def send_request(host, port, request_str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(request_str.encode())
        response = s.recv(4096)
        print("Request:")
        print(request_str.replace("  ", "[SP][SP]"))  # visualize spaces
        print("Response:")
        print(response.decode())
        print("-" * 40)


def build_post_request(path, content):
    return f"POST {path} Content-Length {len(content)}  {content}"


def build_get_request(path):
    return f"GET {path}  "


def build_delete_request(path):
    return f"DELETE {path}  "


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_client.py <port>")
        sys.exit(1)

    HOST = "localhost"
    PORT = int(sys.argv[1])

    # Basic setup
    send_request(HOST, PORT, build_post_request("/key/test", "HelloWorld"))
    send_request(HOST, PORT, build_post_request("/counter/test", "2"))

    # Valid GET - counter should decrease from 2 to 1
    send_request(HOST, PORT, build_get_request("/key/test"))
    # Valid GET - counter should decrease from 1 to 0 and delete the key
    send_request(HOST, PORT, build_get_request("/key/test"))
    # Invalid GET - key no longer exists
    send_request(HOST, PORT, build_get_request("/key/test"))

    # Invalid GET - key never inserted
    send_request(HOST, PORT, build_get_request("/key/invalid"))

    # Invalid DELETE on non-existent counter
    send_request(HOST, PORT, build_delete_request("/counter/invalid"))

    # Invalid POST to counter with missing key in /key/
    send_request(HOST, PORT, build_post_request("/counter/ghost", "3"))

    # Insert key again, add counter, then attempt to POST to /key/ (should fail)
    send_request(HOST, PORT, build_post_request("/key/locked", "Secret"))
    send_request(HOST, PORT, build_post_request("/counter/locked", "1"))
    send_request(HOST, PORT, build_post_request("/key/locked", "NewSecret"))

    # Clean up
    send_request(HOST, PORT, build_delete_request("/counter/locked"))
    send_request(HOST, PORT, build_delete_request("/key/locked"))
