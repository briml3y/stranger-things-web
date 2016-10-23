import ConfigParser
import Queue
import threading
import atexit
from flask import Flask, render_template, request

POOL_TIME = 5  # Seconds

# variables that are accessible from anywhere
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
watchThread = threading.Thread()


def create_app():
    app = Flask(__name__)

    textQueue = Queue.Queue()

    @app.route('/', methods=['GET', 'POST'])
    def form():
        if request.method == 'GET':
            return render_template('index.html')
        elif request.method == 'POST':
            text = request.form['text']
            #print text
            textQueue.put(text)
            #print textQueue.qsize()
        return render_template('index.html', text=text)

    def interrupt():
        global watchThread
        watchThread.cancel()

    def watchQueue():
        global commonDataStruct
        global watchThread
        with dataLock:
        # Do your stuff with commonDataStruct Here
            print "Checking Queue"
            text = textQueue.get()
            print text
            textQueue.task_done()
        # Set the next thread to happen
        watchThread = threading.Timer(POOL_TIME, watchQueue, ())
        watchThread.start()

    def initiateWatchQueue():
        # Do initialisation stuff here
        global watchThread
        # Create your thread
        watchThread = threading.Timer(POOL_TIME, watchQueue, ())
        watchThread.start()

    # Initiate
    initiateWatchQueue()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app


app = create_app()
