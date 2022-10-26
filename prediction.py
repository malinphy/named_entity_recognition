# -*- coding: utf-8 -*-
"""SciBERT demo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HUoQiRKgwlTfZv44ZT8vrJqtSY9B2sXE
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install --quiet tensorflow-text
!pip install --quiet tokenizers
import numpy as np 
import pandas as pd 
import pickle
import tensorflow as tf 
from tensorflow import keras 

from data_loader import load_sentences,list_maker
from helper_functions import tag_encoder
from token_functions import token_aligner,encoder,tag_encoder_2,padder

from model import ner_model
import matplotlib.pyplot as plt
import seaborn as sns


a_file = open("enc_2tags.pkl", "rb")
enc_2tags = pickle.load(a_file)

test_sentence = ['CRICKET - LEICESTERSHIRE TAKE OVER AT TOP AFTER INNINGS VICTORY .']
test_tags = 'O O B-ORG O O O O O O O O'

def prediction(test_sentence):
    input_len = 128
    ids, type_ids, attention_mask,tokens,ids_len = encoder(test_sentence)
    pad_ids = padder(ids,input_len)
    bert_ner_model = ner_model(9)
    bert_ner_model.load_weights('./model_weights/bert_ner_weights.h5')
    p = bert_ner_model.predict(np.array(test_sentence));

    pred_args = tf.math.top_k(p[0][0:len(np.where(pad_ids != 0)[1])], k =1)[1]

    toks = []
    for j,i in enumerate(np.array(tf.math.top_k(p[0][0:len(pad_ids[0][1:len(np.where(pad_ids != 0)[1])-1])],k=1)[1])):
    # print(j,i)
        toks.append(enc_2tags[int(i)])
    # print(ids_len)
    # print(len(pad_ids[0][1:len(np.where(pad_ids != 0)[1])-1]))
    print(tokens[1:-1])
    return((toks))

print(prediction(test_sentence))

