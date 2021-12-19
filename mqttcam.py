import socket
import time
import picamera

def log(txt):
    print(txt, flush=True)

log("Starting mqttcam")

camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30
camera.annotate_background = True
camera.annotate_text = 'Mogwai weight: 5900g, ate: 5.4g'

# server_socket = socket.socket()
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
# server_socket.bind(('0.0.0.0', 3333))
# server_socket.listen(0)
#
# # Accept a single connection and make a file-like object out of it
# log("Listening")
# connection = server_socket.accept()[0].makefile('wb')
# log("accepted")
# try:
#     camera.start_recording(connection, format='h264')
#     camera.wait_recording(60)
#     camera.stop_recording()
# finally:
#     connection.close()
#     server_socket.close()



# import asyncio
#
# async def handle_echo(reader, writer):
#     log("Client connected")
#     camera.start_recording(writer, format='h264')
#     # while True:
#     log("M")
#     await server.wait_closed()
#     server.
#         # try:
#         #     camera.wait_recording(1)
#         # except Exception as e:
#         #     log(str(e))
#         # await asyncio.sleep(1)
#
#     log("Client disconnected")
#
#
#
# async def main():
#     global server
#     server = await asyncio.start_server(
#         handle_echo, '0.0.0.0', 3333)
#
#     addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
#     log(f'Serving on {addrs}')
#
#     async with server:
#         log("yo")
#         await server.serve_forever()
#
# asyncio.run(main())





import asyncio


class CamServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log('Connection from {}'.format(peername))
        self.transport = transport
        camera.start_recording(transport, format='h264')

    def connection_lost(self, exc):
        log('Disconnected: {}'.format(exc))
        camera.stop_recording()


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: CamServerProtocol(),
        '0.0.0.0', 3333)

    async with server:
        await server.serve_forever()


asyncio.run(main())
