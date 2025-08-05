# Lightweight HTTP-like Key-Value Server

This is a lightweight TCP server that implements a custom HTTP-like protocol, supporting an in-memory key-value store with an optional retrieval-limiting counter system.

It is designed for educational and experimentation purposes to help understand socket programming, persistent connections, and request parsing without relying on web frameworks.

---

## Features

- Built with Python and `socket`
- Custom lightweight HTTP-like protocol
- Persistent connections (similar to HTTP/1.1)
- Two endpoints:
  - `/key/<key>`: General-purpose key-value store
  - `/counter/<key>`: Tracks limited retrievals for temporary keys
- Supports:
  - `POST` for insertion/update
  - `GET` for retrieval
  - `DELETE` for deletion
- In-memory only (no database or disk writes)

---

## Endpoints & Behavior

### `/key/<key>`

- `POST`: Inserts or updates a value for the key.
  - Fails with `405 MethodNotAllowed` if key is temporary (has counter).
- `GET`: Retrieves the value.
  - If the key is temporary, the associated counter is decremented.
  - If the counter reaches 0, the key is deleted automatically.
- `DELETE`: Deletes the key.
  - Fails with `405 MethodNotAllowed` if key is temporary.

### `/counter/<key>`

- `POST`: Adds or increases the counter for a key.
  - Only works if the key exists in `/key/`.
- `GET`: Returns:
  - The remaining retrieval count if temporary
  - `"Infinity"` if the key exists but is permanent
  - `404 NotFound` if key doesn't exist
- `DELETE`: Removes the counter, making the key permanent.

---

### Request Format

A request consists of:

1. A **header** made up of whitespace-separated substrings:
   - The first two substrings are mandatory:
     - HTTP method (`GET`, `POST`, `DELETE`) — case-insensitive
     - Path — case-sensitive
   - Optional header fields (e.g., `Content-Length`) follow in pairs.
   - The header ends with **two whitespace characters**.
2. An optional **content body**, included only if `Content-Length` is specified.
3. Requests are separated by two space characters (ASCII 0x20).

**Example request**:

```
GET /key/ThisIsMyKey  POST /key/ThisIsMyKey Content-Length 11 Hello World!  POST /counter/CS2105 Content-Length 1 3
```

---

### Response Format

A response consists of:

1. A **status line** with two required fields:
   - Status code (e.g., `200`, `404`, `405`)
   - Status description (e.g., `OK`, `NotFound`, `MethodNotAllowed`)
2. Optional header fields (e.g., `Content-Length`) for responses with content.
3. Optional content body, if applicable.
4. Responses are separated by two space characters.

**Example response**:

```
404 NotFound  200 OK  200 OK Content-Length 11 Hello World!  200 OK Content-Length 1 2  405 MethodNotAllowed   200 OK Content-Length 8 Infinity
```

## Protocol Summary

| Component     | Format Description                                                                    |
| ------------- | ------------------------------------------------------------------------------------- |
| **Request**   | `METHOD PATH [HeaderKey HeaderVal] [HeaderKey HeaderVal]  ␣␣ [Content]`               |
| **Response**  | `STATUS_CODE StatusText [HeaderKey HeaderVal]  ␣␣ [Content]`                          |
| **Delimiter** | Two ASCII space characters (`␣␣`, i.e. `0x20 0x20`) used to separate headers and body |

> Notes:
>
> - `METHOD` is case-insensitive (e.g., GET, POST, DELETE)
> - `PATH` is case-sensitive (e.g., `/key/CS`)
> - `Content-Length` must be included if content is present
> - Multiple requests/responses may be sent in a single TCP stream as long as they follow the delimiter rule

---

### Example Request and Response received

Request sent in one TCP stream:

```
POST /key/CS Content-Length 11 Hello World  POST /counter/CS Content-Length 1 3  GET /key/CS  GET /counter/CS  DELETE /counter/CS  GET /counter/CS  GET /key/InvalidKey
```

Response received in one TCP stream:

```
200 OK  200 OK  200 OK Content-Length 11 Hello World  200 OK Content-Length 1 2  200 OK  200 OK Content-Length 8 Infinity  404 NotFound
```

---

## Getting Started

### Requirements

- Python 3.10+

### Running the Server

```bash
python3 http_server.py <port>
```

Replace `<port>` with any available port number.

### Testing

#### Option 1: Use the Python Test Client

You can run the included `test_client.py` script to automatically test the server's functionality.

```bash
python3 http_server.py 8080  # in one terminal
python3 test_client.py 8080  # in another terminal
```

This will test:

- Basic key-value insertion and retrieval
- Counter behavior and auto-deletion
- Invalid operations (404 and 405 responses)
- Edge cases like missing keys or modification of temporary keys

#### Option 2: Manual Testing with `netcat`

```bash
printf "POST /key/test Content-Length 10  HelloWorld" | nc localhost 8080
```

Other examples:

```bash
printf "POST /counter/test Content-Length 1  3" | nc localhost 8080
printf "GET /key/test  " | nc localhost 8080
printf "GET /counter/test  " | nc localhost 8080
printf "DELETE /counter/test  " | nc localhost 8080
printf "DELETE /key/test  " | nc localhost 8080
```

---

## Concepts Demonstrated

- Raw TCP socket programming
- Persistent connections
- Custom protocol design
- Stateful in-memory data stores
- Protocol-compliant request parsing and chunk handling

---

## License

This project is open-source under the MIT License.
