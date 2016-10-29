# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
import signal
import sys
import ConfigParser
import Queue
import threading
import logging
import time
from amqpy import Connection, Message, AbstractConsumer, Timeout
from neopixel import *

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
timeBetweenMessages=1
drainWait=.55555
exitFlag=0

LED_COUNT      = 100      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

red=Color(255, 0, 0)
blue=Color(0, 255, 0)
green=Color(0, 0, 255)
shift=int(-1)
timeBeteenLetters=1
waiting=1
shotFlashCount=5
shotWaitTimeCount=.50

class Consumer(AbstractConsumer):
    def run(self, msg):
        logging.debug('Received a message: {}'.format(msg.body))
        logging.debug('Adding to queue')
        queue.put(msg.body)
        logging.debug('Acknowledge message')
        msg.ack()


def messageQueueWatcher():
    while True:
        # wait for events, which will receive delivered messages and call any consumer callbacks
        conn.loop(timeout=drainWait)
        if exitFlag:
            break

def textQueueWatcher():
    global waiting
    global waitingThread
    while True:
        # logging.trace('ExitFlag is %d', exitFlag)
        message=None
        try:   
            message=queue.get_nowait()
        except:
            pass 
        if message:
            displayMessage(message)
            if queue.qsize() > 0:
                waiting=0;
                logging.debug('Pausing for %d seconds', timeBetweenMessages)
                time.sleep(timeBetweenMessages)
        else:
            if  waitingThread and not waitingThread.isAlive():
                waitingThread=threading.Thread(target=waitingDisplay)
                waitingThread.setDaemon(True)
                waitingThread.start()
        if exitFlag:
            break

def displayMessage(message):
    global waiting
    global waitingThread
    if waitingThread and waitingThread.isAlive():
        waiting=1
        waitingThread.join()
    if message=='shots':
        displayShots()
    else:
        logging.info('Printing new message: %s', message)
        colorWipe(strip,red,10)
        words=message.split(' ')
        for word in words:
            if word.lower() in alphabetDict:
                numbers=alphabetDict.get(word.lower())
                logging.debug('Found matching numbers %s', numbers)
                colorClear()
                for number in numbers.split(','):
                    strip.setPixelColor(int(number)+shift,Color(255, 0, 0))
                strip.show()
                time.sleep(timeBeteenLetters)

            else:
                for c in word:
                    logging.debug('Checking character: %s', c)
                    if c.lower() in alphabetDict:
                        numbers=alphabetDict.get(c.lower())
                        logging.debug('Found matching numbers %s', numbers)
                        colorClear()
                        for number in numbers.split(','):
                            strip.setPixelColor(int(number)+shift,Color(255, 0, 0))
                    strip.show()
                    time.sleep(timeBeteenLetters)
    colorClear()
    strip.show()

def displayShots():
    numbers=alphabetDict.get('shots')
    logging.debug('Found matching numbers %s', numbers)

    colorClear()
    strip.show()
    for number in numbers.split(','):
        strip.setPixelColor(int(number)+shift,Color(255, 0, 0))
        strip.show()
    time.sleep(shotWaitTimeCount)
    for number in numbers.split(','):
        strip.setPixelColor(int(number)+shift,Color(0, 255, 0))
    strip.show()
    time.sleep(shotWaitTimeCount)
    for number in numbers.split(','):
        strip.setPixelColor(int(number)+shift,Color(0, 0, 255))
    strip.show()
    time.sleep(shotWaitTimeCount)
    for number in numbers.split(','):
        strip.setPixelColor(int(number)+shift,Color(0, 255, 0))
    strip.show()
    time.sleep(shotWaitTimeCount)
    for number in numbers.split(','):
        strip.setPixelColor(int(number)+shift,Color(255,0, 0))
    strip.show()
    time.sleep(shotWaitTimeCount)
    colorClear()
    strip.show()



def waitingDisplay():
    while True:
        rainbow(strip);
        if waiting or exitFlag:
            break

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    # """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def colorClear():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
        strip.show()

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(((i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def signal_handler(signal, frame):
    global exitFlag
    global waiting
    print('You pressed Ctrl+C!')
    exitFlag=1
    waiting=1
    waitingThread.join()
    msgQueueThread.join()
    msgQueueThread.join()
    sys.exit(0)

if __name__ == '__main__':


    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    alphabetDict=dict(config.items('alphabet'))
    # for k, v in alphabetDict.items():
    #     print(k, v)

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    # # Intialize the library (must be called once before other functions).
    strip.begin()

    ampqExchange=config.get('ampq','exchange')
    ampqQueue=config.get('ampq','queue')

    conn = Connection()  # connect to guest:guest@localhost:5672 by default

    ch = conn.channel()

    # declare an exchange and queue, and bind the queue to the exchange
    ch.exchange_declare(ampqExchange, 'direct')
    ch.queue_declare(ampqQueue)
    ch.queue_bind(ampqQueue, exchange=ampqExchange, routing_key=ampqQueue)

    consumer = Consumer(ch, ampqQueue)
    consumer.declare()

    queue = Queue.Queue()

    waitingThread=threading.Thread(target=waitingDisplay)

    msgQueueThread = threading.Thread(target=messageQueueWatcher)
    msgQueueThread.setDaemon(True)
    msgQueueThread.start()

    textQueueThread = threading.Thread(target=textQueueWatcher)
    textQueueThread.setDaemon(True)
    textQueueThread.start()

    # queue.put('test')
    # time.sleep(40)
    # logging.debug('Setting exit flag to 1')
    # exitFlag=1
    # time.sleep(5)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    signal.pause()
