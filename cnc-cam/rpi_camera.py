# Sources:
# https://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver

from threading import Condition
from string import Template
from http import server
from subprocess import check_output

# template for html status output
PAGE = """\
<html>
<head>
    <title>CNC Monitoring</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
    <style>
        .debug-info {
            padding: 1rem;
        }
    </style>
</head>
<body>
    <article>
        <h1>CNC Monitoring</h1>
        <img src="stream.mjpg" style="width: 100%;" />
    </article>
    <article>
        <h2>Debug</h2>
        <b>USB Devices</b>
        <pre class="debug-info"><samp>$usb</samp></pre>
        <b>USB IP Devices</b>
        <pre class="debug-info"><samp>$usbip</samp></pre>
    </article>
</body>
</html>
"""

# configuration
PORT = 8000
CAMERA_ORIENTATION = 180

# camera output 
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

# handler for image streaming and debug info
class StreamingHandler(server.BaseHTTPRequestHandler):
    # get debug information about USB devices
    usbDevices = check_output(["lsusb"]).decode().rstrip()
    usbIpDevices = check_output(["usbip", "list", "-p", "-l"]).decode().rstrip()

    # streaming part / sending response to webclient
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = Template(PAGE).substitute(usb=self.usbDevices, usbip=self.usbIpDevices).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

# web server configuration
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# bootstrap application, start camera feed and webserver
with picamera.PiCamera(resolution='1920x1080', framerate=24) as camera:
    camera.rotation = CAMERA_ORIENTATION
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', PORT)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
