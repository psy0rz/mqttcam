import asyncio
import json
import os

import asyncio_mqtt
import picamera

import config
import upload
from log import log

log("Starting mqttcam")

camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30
camera.annotate_background = True
camera.annotate_text_size=40

streaming=False

# streaming server stuff
class CamServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log('Viewer client connection from {}'.format(peername))
        self.transport = transport
        global streaming
        streaming=True
        camera.start_recording(transport, format='h264', sei=True, intra_period=0)

    def connection_lost(self, exc):
        log('Viewer client disconnected: {}'.format(exc))
        global streaming
        streaming=False
        camera.stop_recording()



async def mqtt_server():

    # async def mqtt_error(text):
    #     await client.publish(config.mqtt_topic + "error", text)


    # handle mqtt stuff
    will=asyncio_mqtt.Will(config.mqtt_topic+"status", "offline")
    async with asyncio_mqtt.Client(config.mqtt_server, will=will) as client:
        global streaming

        await client.publish(config.mqtt_topic+"status", "online")

        async with client.unfiltered_messages() as messages:

            await client.subscribe(config.mqtt_topic+"#")
            log("Connected to mqtt server")

            async for message in messages:

                if message.topic.endswith("/annotate_text"):
                    camera.annotate_text=message.payload.decode()
                    log("Changed annotate text: {}".format(message.payload.decode()))

                elif not streaming:
                    if message.topic.endswith("/start"):
                        if not camera.recording:
                            file_name=config.upload_dir+"current.h264"
                            log("Started recording")
                            camera.start_recording(file_name, format='h264', sei=True, intra_period=0)

                    elif message.topic.endswith("/stop"):
                        if camera.recording:
                            log("Stopped recording")
                            camera.stop_recording()

                    elif message.topic.endswith("/upload"):
                        log("Moving video to upload dir")
                        if camera.recording:
                            camera.stop_recording()
                        try:

                            params=json.loads(message.payload.decode())
                            name=params['title']
                            os.rename(config.upload_dir+"current.h264", config.upload_dir+name+".h264")
                            with open(config.upload_dir+name+".meta","w") as fh:
                                fh.write(message.payload.decode())
                        except Exception as e:
                            log("Error: "+str(e))

async def main():

    #cam server
    loop = asyncio.get_running_loop()
    server  = loop.create_server(
        lambda: CamServerProtocol(),
        '0.0.0.0', 3333)

    #mqtt server
    await asyncio.gather(server, mqtt_server())

asyncio.run(main())
