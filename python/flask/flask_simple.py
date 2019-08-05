from flask import Flask, url_for
app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Welcome'

@app.route('/light_on/<color>')
def light_on(color):
    resp = 'Light_on: color not supported: ' + color
    if color == 'red':
        resp = "Turned on red..."
    elif color == 'orange':
        resp = "Turned on orange..."
    elif color == 'blue':
        resp = "Turned on blue..."
    elif color == 'green':
        resp = "Turned on green..."
    return resp

if __name__ == '__main__':
    app.run()

'''

Test with:

import requests

r = requests.get('http://localhost:5000/light_on/red')
print(r.text)
'''