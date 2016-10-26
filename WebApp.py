# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
import ConfigParser
from amqpy import Connection, Message
from flask import Flask, render_template, request

# Initialize the Flask application
app = Flask(__name__)


alphabetDict=dict(config.items('alphabet'))
# for k, v in alphabetDict.items():
#     print(k, v)

# Define a route for the default URL, which loads the form
@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        text = request.form['text']
        print text;
        ch.basic_publish(Message(text), exchange='strangerthings', routing_key='text.queue')
    return render_template('index.html', text=text)

# Run the app :)
if __name__ == '__main__':

    conn = Connection()  # connect to guest:guest@localhost:5672 by default

    ch = conn.channel()

    # declare an exchange and queue, and bind the queue to the exchange
    ch.exchange_declare('strangerthings', 'direct')
    ch.queue_declare('text.queue')
    ch.queue_bind('text.queue', exchange='strangerthings', routing_key='text.queue')

    config = ConfigParser.ConfigParser()
    config.read('config.ini')


    #TODO Add logging here
    host=config.get('web', 'host', 0)
    port=config.getint('web', 'port')

    app.run(
      host=host,
      port=port
    )

