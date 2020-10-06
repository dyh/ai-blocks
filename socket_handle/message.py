# coding:utf-8

import io
import sys
import cv2
import json
import struct


class Message:
    def __init__(self, sock, addr):
        self._sock = sock
        self._addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader = None
        self._jsonheader_len = None
        self._response_created = False
        self._request = None

    def get_result(self):
        return self._request

    def clear(self):
        self._jsonheader = None
        self._jsonheader_len = None
        self._response_created = False
        self._request = None
        pass

    def _socket_read(self):
        try:
            # Should be ready to read
            data = self._sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("remote socket closed.")
            pass
        pass

    def _socket_write(self):
        if self._send_buffer:
            # print("sending", repr(self._send_buffer), "to", self.addr)
            print("sending", str(len(self._send_buffer)), "buffer to", self._addr)
            try:
                # Should be ready to write
                sent = self._sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
            pass

    @staticmethod
    def _json_encode(obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    @staticmethod
    def _json_decode(json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(self, *, content_bytes, content_type, content_encoding):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack("<H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def read(self):
        while self._request is None:
            self._socket_read()

            if self._jsonheader_len is None:
                self._process_proto_header()

            if self._jsonheader_len is not None:
                if self._jsonheader is None:
                    self._process_json_header()

            if self._jsonheader:
                if self._request is None:
                    self._process_request()
                    pass
                pass
            pass
        pass

    def write(self, image_object=None, text_message=None):
        # if self._request:
        if not self._response_created:
            ret, img_encode = cv2.imencode('.png', image_object)
            str_encode = img_encode.tostring()

            if text_message is not None:
                # create text/json message
                content = {"result": text_message}
                content_encoding = "utf-8"
                response = {
                    "content_bytes": self._json_encode(content, content_encoding),
                    "content_type": "text/json",
                    "content_encoding": content_encoding,
                }
                message = self._create_message(**response)
                self._send_buffer += message

            if image_object is not None:
                # create binary/image message
                response = {
                    "content_bytes": str_encode,
                    "content_type": "binary/image",
                    "content_encoding": 'binary',
                }
                message = self._create_message(**response)
                self._send_buffer += message

            # change the flag
            self._response_created = True

        # send buffer to socket
        self._socket_write()

    def _process_proto_header(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack("<H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
            pass
        pass

    def _process_json_header(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader = self._json_decode(self._recv_buffer[:hdrlen], "utf-8")
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in ("byteorder", "content-length", "content-type", "content-encoding",):
                if reqhdr not in self._jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')
                pass
            pass
        pass

    def _process_request(self):
        content_len = self._jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        if self._jsonheader["content-type"] == "text/json":
            encoding = self._jsonheader["content-encoding"]
            self._request = self._json_decode(data, encoding)
            # print("received request", repr(self._request), "from", self._addr)
        elif self._jsonheader["content-type"] == "binary/image":
            # binary/image content-type
            self._request = data
            pass
        pass

        print(f'received {self._jsonheader["content-type"]} request from', self._addr, ", length:", content_len, )
