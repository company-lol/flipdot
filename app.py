import logging
import asyncio
from os import path

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1, QOS_2
from flipdotapi import remote_sign as sign

import configparser
import logging


@asyncio.coroutine
def mqtt_listener():
    C = MQTTClient()
    yield from C.connect(mqtt_broker)

    yield from C.subscribe([
        (mqtt_topic, QOS_1)
         ])
    try:
        while True:
            message = yield from C.deliver_message()
            packet = message.publish_packet
            logger.debug("%s => %s" % ( packet.variable_header.topic_name, str(packet.payload.data)))
            text = packet.payload.data.decode()
            logging.debug(text)
            sign.write_text(text, font_name=display_font)
        yield from C.unsubscribe([mqtt_topic])
        yield from C.disconnect()
    except ClientException as ce:
        logger.error("Client exception: %s" % ce)



if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)
    logger = logging.getLogger(__name__)

    hbmqtt_log = logging.getLogger("hbmqtt")
    hbmqtt_log.setLevel(logging.DEBUG)

    config = configparser.ConfigParser()
    config_file = 'config.ini'
    if path.exists(config_file):
        config.read(config_file)
    else:
        logging.error("Config file missing: {}".format(config_file))
        sys.exit(1)

    sign_url = config.get('FLIPDOT_SERVER', 'URL')
    sign_columns = config.getint('FLIPDOT_SERVER', 'COLUMNS')
    sign_rows = config.getint('FLIPDOT_SERVER', 'ROWS')
    sign_sim = config.getboolean('FLIPDOT_SERVER', 'SIMULATOR')

    display_font = config.get('DISPLAY', 'FONT')

    mqtt_broker = config.get('MQTT', 'BROKER')
    mqtt_topic = config.get('MQTT', 'TOPIC')

    sign = sign(sign_url, sign_columns, sign_rows, simulator=sign_sim)
    
    logger.debug("Start event loop")

    asyncio.get_event_loop().run_until_complete(mqtt_listener())
