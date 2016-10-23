# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
import ConfigParser, Queue, time
from flask import Flask, render_template, request, url_for
from threading import Thread

# Initialize the Flask application
app = Flask(__name__)


POOL_TIME = 5
# config = ConfigParser.ConfigParser()
# config.read('config.ini')
#
# #TODO Add logging here
# host=config.get('web', 'host', 0)
# port=config.getint('web', 'port')
#
# alphabetDict=dict(config.items('alphabet'))
# # for k, v in alphabetDict.items():
# #     print(k, v)

watchThread = Thread(target=watchQueue, args=(textQueue))
watchThread.start()

# Define a route for the default URL, which loads the form
@app.route('/', methods=['GET', 'POST'])
def form():

    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        text = request.form['text']
        print text;
        textQueue.put(text)
        print textQueue.qsize()
    return render_template('index.html', text=text)

def watchQueue(queue):
    while True:
        print "Checking Queue"
        print queue.get()
        time.sleep(2)
        queue.task_done()

# Run the app :)
# if __name__ == '__main__':


