
# coding: utf-8

# In[1]:


import os
import time
import warnings
import numpy as np
from numpy import newaxis
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential


# In[3]:


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")


# In[4]:


def load_data(filename, seq_len, normalise_window):
    f = open(filename, 'rb').read()
    data = f.decode().split('\n')
    
    sequence_length = seq_len + 1
    result = []
    for index in range(len(data) - sequence_length):
        result.append(data[index: index + sequence_length])
        
    if normalise_window:
        result = normalise_window(result)
        
    result = np.array(result)
    
    row = round(0.9 * result.shape[0])
    train = result[:int(row),:]
    np.random.shuffle(train)
    x_train = train[:,:-1]
    y_train = train[: -1]
    x_test = result[int(row):, :-1]
    y_test = result[int(row):, -1]
    
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    return [x_train, y_train, x_test, y_test]


# In[5]:


def normalise_windows(window_data):
    normalised_data = []
    for window in window_data:
        normalised_window = [((float(p) / float(window[0])) - 1) for p in window]
        normalise_data.append(normalised_window)
    return normalised_data


# In[6]:


def build_model(layers):
    model = Sequential()
    
    model.add(LSTM(input_shape = (layers[1], layers[0]),
                  output_dim = layers[1],
                  return_sequences=True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(layers[2], return_sequences=False))
    model.add(Dropout(0.2))
    
    model.add(Dense(output_dim = layer[3]))
    model.add(Activation("Linear"))
    
    start = time.time()
    mdoel.compile(loss="mse", optimizer = 'rmprop')
    print("実行時間：　", time.time() - start)
    return model


# In[7]:


def predict_point_by_point(model, data):
    predicted = model.predict(data)
    predicted = no.reshape(predicted, (predicted.size,))
    return predicted


# In[8]:


def predict_sequence_full(model, data, window_size):
    curr_frame = daa[0]
    predicted = []
    for i in range(len(data)):
        predicted.append(model.predict(curr_frame[newaxis,:,:])[0,0])
        curr_frame = curr_frame[1:]
        curr_frame = np.insert(curr_frame, [window_size-1], predicted[-1], axis=0)
    return predicted


# In[9]:


def predict_sequences_multipule(model, data, window_size, prediction_len):
    prediction_len = []
    for i in range(len(data)/prediction_len):
        curr_frame = data[i*prediction_len]
        predicted = []
        for j in xrange(prediction_len):
            predicted.append(model.predict(curr_frame[newaxis, :, :][0,0]))
            curr_frame = curr_frame[1:]
            curr_frame = np.insert(curr_frame, [window_size-1], predicted[-1], axis=0)
        prediction_seqs.append(predicted)
    return prediction_seqs


# In[12]:


#import subprocess
#subprocess.run(['jupyter', 'nbconvert', '--to', 'python', 'ファイル名.ipynb'])

