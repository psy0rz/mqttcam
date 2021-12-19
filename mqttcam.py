import asyncio_mqtt
import picamera
import asyncio

import config


def log(txt):
    print(txt, flush=True)


log("Starting mqttcam")

camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30
camera.annotate_background = True

streaming=False

# streaming server stuff
class CamServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log('Cam client connection from {}'.format(peername))
        self.transport = transport
        global streaming
        streaming=True
        camera.start_recording(transport, format='h264')

    def connection_lost(self, exc):
        log('Cam client disconnected: {}'.format(exc))
        global streaming
        streaming=False
        camera.stop_recording()



async def mqtt_server():

    async def mqtt_error(text):
        await client.publish(config.mqtt_topic + "error", text)

    # handle mqtt stuff
    will=asyncio_mqtt.Will(config.mqtt_topic+"status", "offline")
    async with asyncio_mqtt.Client(config.mqtt_server, will=will) as client:
        global streaming

        await client.publish(config.mqtt_topic+"status", "online")

        async with client.unfiltered_messages() as messages:

            await client.subscribe(config.mqtt_topic+"#")
            async for message in messages:

                if message.topic.endswith("/annotate_text"):
                    camera.annotate_text=message.payload.decode()

                if not streaming:
                    if message.topic.endswith("/start"):
                        if not camera.recording:
                            camera.start_recording("/tmp/mqttcam.mp4", format='h264')

                    elif message.topic.endswith("/stop"):
                        if camera.recording:
                            camera.stop_recording()

                    # elif message.topic.endswith("/upload"):
                    # https://developers.google.com/youtube/v3/guides/uploading_a_video
                    # https://pypi.org/project/simple-youtube-api/
async def main():

    #cam server
    loop = asyncio.get_running_loop()
    server  = loop.create_server(
        lambda: CamServerProtocol(),
        '0.0.0.0', 3333)

    #mqtt server
    await asyncio.gather(server, mqtt_server())

asyncio.run(main())
