# app.py - a minimal flask api using flask_restful
from gevent import monkey
monkey.patch_all()

import tflearn
import pickle
from tflearn.data_utils import *

from threading import Thread
from threading import Lock
from queue import Queue

from flask import Flask, jsonify
from gevent import pywsgi
from flask_restful import Resource, Api
from flask_cors import CORS
from flask import Response
from flask import request

app = Flask(__name__)
app.config.update(
        TESTING=False,
        DEBUG=False,
        ENV='production')
api = Api(app)
CORS(app)

maxlen = 25

class ModelLoader:
    _base = None
    _char_idx = None
    _g = None
    _m = None
    _thread = None
    _inputQueue = Queue()
    _outputQueue = Queue()
    _queueLock = Lock()
    _isStopped = False

    def __init__(self, name):
        self._thread = Thread(name=self._base, target=self.thread_run)
        self._base = name
        self._thread.start()

    def thread_run(self):
        self._base = self._base
        print("loading "+"char_idx_"+self._base+".pickle")
        self._char_idx = pickle.load(open("ML/"+self._base+"/char_idx_"+self._base+".pickle", 'rb'))
        print("loading "+self._base+".txt")
        # _,_,self._char_idx = textfile_to_semi_redundant_sequences(self._base+".txt", seq_maxlen=maxlen, redun_step=3, pre_defined_char_idx=self._char_idx)
        self._g = tflearn.input_data([None, maxlen, len(self._char_idx)])
        self._g = tflearn.lstm(self._g, 512, return_seq=True)
        self._g = tflearn.dropout(self._g, 0.5)
        self._g = tflearn.lstm(self._g, 512, return_seq=True)
        self._g = tflearn.dropout(self._g, 0.5)
        self._g = tflearn.lstm(self._g, 512)
        self._g = tflearn.dropout(self._g, 0.5)
        self._g = tflearn.fully_connected(self._g, len(self._char_idx), activation='softmax')
        self._g = tflearn.regression(self._g, optimizer='adam', loss='categorical_crossentropy', learning_rate=0.001)
        self._m = tflearn.SequenceGenerator(self._g, dictionary=self._char_idx,
                                      seq_maxlen=maxlen,
                                      clip_gradients=5.0,
                                      checkpoint_path="ML/"+self._base+"/model_"+self._base)
        print("Loading "+"ML/"+self._base+"/"+self._base+'.tfl')
        self._m.load("ML/"+self._base+"/"+self._base+'.tfl')
        while not self._isStopped:
            data = self._inputQueue.get()
            self._queueLock.acquire(blocking=True)

    def fstring(self,seed=''):
        rand = " " + random_sequence_from_textfile("ML/"+self._base+".txt", maxlen)
        s = '{:25.25}'.format(seed + rand)
        print("using seed\n"+s)
        return s

    def generate(self,seed, size=100, temperature=0.5):
        return self._m.generate(size, temperature, seq_seed=self.fstring(seed))


modelContes = ModelLoader('contes')
modelShak = ModelLoader('shakespeare')
modelSher = ModelLoader('sherlock')
modelGr1Fun = ModelLoader('gr1fun')
modelCook = ModelLoader('cook')

# m.fit(X, Y, validation_set=0.1, batch_size=128, n_epoch=1, run_id='contes')
@app.route('/')
def model():
    return modelContes.generate('le sultan',100,0.5)


@app.route('/contes/g/<seed>/<size>')
def cgen(seed=None, size=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    return modelContes.generate(seed,s,0.5)

@app.route('/cook/g/<seed>/<size>')
def ogen(seed=None, size=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    return modelCook.generate(seed,s,0.5)

@app.route('/contes/g/<seed>/<size>/<temp>')
def cgentemp(seed=None, size=None, temp=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    try:
        t = float(temp)
    except ValueError:
        t = 0.5
    return modelContes.generate(seed,s,t)


@app.route('/shakespeare/g/<seed>/<size>')
def bgen(seed=None, size=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    return modelShak.generate(seed,s,0.5)


@app.route('/shakespeare/g/<seed>/<size>/<temp>')
def bgentemp(seed=None, size=None, temp=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    try:
        t = float(temp)
    except ValueError:
        t = 0.5
    return modelShak.generate(seed,s,t)

@app.route('/sherlock/g/<seed>/<size>')
def sgen(seed=None, size=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    return modelSher.generate(seed,s,0.5)


@app.route('/sherlock/g/<seed>/<size>/<temp>')
def sgentemp(seed=None, size=None, temp=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    try:
        t = float(temp)
    except ValueError:
        t = 0.5
    return modelSher.generate(seed,s,t)


@app.route('/conte', methods=['POST'])
def gen_contes():
    if request.is_json:
        print("JSON")
    else:
        print(request)
	
    data = request.get_json(force=True) # json dict
    seed = data["seed"]
    try:
        size = int(data['size'])
    except (ValueError, KeyError):
        size = 100
    if(size == None):
        size = 100
    try:
        temp = float(data['temp'])
    except (ValueError, KeyError):
        temp = 0.5
    if(temp == None):
        temp = 0.5
    r = modelContes.generate(seed,size,temp)
    print(r)
    return Response(r, mimetype='text/plain')

@app.route('/shakespeare', methods=['POST'])
def gen_shakespeare():
    data = request.get_json(force=True) # json dict
    seed = data["seed"]
    try:
        size = int(data['size'])
    except (ValueError, KeyError):
        size = 100
    if(size == None):
        size = 100
    try:
        temp = float(data['temp'])
    except (ValueError, KeyError):
        temp = 0.5
    if(temp == None):
        temp = 0.5
    r = modelShak.generate(seed,size,temp)
    print(r)
    return Response(r, mimetype='text/plain')

@app.route('/sherlock', methods=['POST'])
def gen_sherlock():
    data = request.get_json(force=True) # json dict
    seed = data["seed"]
    try:
        size = int(data['size'])
    except (ValueError, KeyError):
        size = 100
    if(size == None):
        size = 100
    try:
        temp = float(data['temp'])
    except (ValueError, KeyError):
        temp = 0.5
    if(temp == None):
        temp = 0.5
    r = modelSher.generate(seed,size,temp)
    print(r)
    return Response(r, mimetype='text/plain')

@app.route('/gr1fun/g/<seed>/<size>')
def g1fgen(seed=None, size=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    return modelGr1Fun.generate(seed,s,0.5)


@app.route('/gr1fun/g/<seed>/<size>/<temp>')
def g1fgentemp(seed=None, size=None, temp=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    try:
        t = float(temp)
    except ValueError:
        t = 0.5
    return modelGr1Fun.generate(seed,s,t)

@app.route('/cook/g/<seed>/<size>/<temp>')
def cooktemp(seed=None, size=None, temp=None):
    try:
        s = int(size)
    except ValueError:
        s = 100
    try:
        t = float(temp)
    except ValueError:
        t = 0.5
    return modelCook.generate(seed,s,t)

@app.route('/gr1fun', methods=['POST'])
def gen_gr1fun():
    data = request.get_json(force=True) # json dict
    seed = data["seed"]
    try:
        size = int(data['size'])
    except (ValueError, KeyError):
        size = 100
    if(size == None):
        size = 100
    try:
        temp = float(data['temp'])
    except (ValueError, KeyError):
        temp = 0.5
    if(temp == None):
        temp = 0.5
    r = modelGr1Fun.generate(seed,size,temp)
    print(r)
    return Response(r, mimetype='text/plain')

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8280)

server = pywsgi.WSGIServer(('0.0.0.0', 8280), app)
server.serve_forever()
