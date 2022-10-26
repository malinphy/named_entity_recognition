# -*- coding: utf-8 -*-
"""SciBERT demo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HUoQiRKgwlTfZv44ZT8vrJqtSY9B2sXE
"""

# from google.colab import drive
# drive.mount('/content/drive')

# !pip install --quiet tensorflow-text
# !pip install --quiet tokenizers
import numpy as np 
import pandas as pd 
import pickle
import os 
import re
import tensorflow as tf 
from tensorflow import keras 
from tensorflow.keras import Model,Input,layers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import *

import tensorflow_hub as hub 
import tokenizers
from tokenizers import BertWordPieceTokenizer
import tensorflow_text as text 
from tensorflow.keras.preprocessing.sequence import pad_sequences
from platform import python_version
import sklearn 
from sklearn.metrics import f1_score,classification_report,confusion_matrix
from data_loader import load_sentences,list_maker
from helper_functions import tag_encoder
from token_functions import token_aligner,encoder,tag_encoder_2,padder
from model import ner_model
import matplotlib.pyplot as plt
import seaborn as sns

train_path  = './data/train.txt'
test_path = './data/test.txt'
validation_path = './data/valid.txt'

saving_path = './'

input_len =128
epochs = 15
batch = 400

encoder_url = 'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3'
bert_url = 'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-6_H-128_A-2/2'

bert_layer = hub.KerasLayer(bert_url, trainable=True)
vocab_file = bert_layer.resolved_object.vocab_file.asset_path.numpy().decode("utf-8")
tokenizer = BertWordPieceTokenizer(vocab=vocab_file, lowercase=False)

train_set  = load_sentences(train_path)
test_set  = load_sentences(test_path)
validation_set  = load_sentences(validation_path)

print('train_set_length :',len(train_set))
print('test_set_length :',len(test_set))
print('validation_set_length :',len(validation_set))

sentences_train = list_maker(train_set, 0)
tags_train = list_maker(train_set, 1)

sentences_test = list_maker(test_set, 0)
tags_test = list_maker(test_set, 1)

sentences_validation = list_maker(validation_set, 0)
tags_validation = list_maker(validation_set, 1)

j_tags = ' '.join(tags_train)
unique_tags = np.unique(j_tags.split())

num_tags = len(unique_tags) ### number of unique tags
enc_2tags = {i:j for i,j in enumerate(unique_tags)}
tags_2enc = {j:i for i,j in enumerate(unique_tags)}

aligned_tags_train = token_aligner(sentences_train,tags_train)
aligned_tags_val = token_aligner(sentences_validation,tags_validation)

train_ids, train_type_ids, train_attention_mask,train_tokens,ids_len = encoder(sentences_train)
encoded_tags_train = tag_encoder_2(aligned_tags_train,tags_2enc)

val_ids, val_type_ids, val_attention_mask,validation_tokens,ids_len = encoder(sentences_validation)
encoded_tags_val = tag_encoder_2(aligned_tags_val,tags_2enc)

print('number of unique tags :', num_tags)
print('unique tags:', unique_tags)

a_file = open(saving_path+"enc_2tags.pkl", "wb")
pickle.dump(enc_2tags, a_file)
a_file.close()

a_file = open(saving_path+"tags_2enc.pkl", "wb")
pickle.dump(tags_2enc, a_file)
a_file.close()


a_file = open(saving_path+"tags_2enc.pkl", "rb")
tags_2enc = pickle.load(a_file)
print(tags_2enc)

a_file = open(saving_path+"enc_2tags.pkl", "rb")
enc_2tags = pickle.load(a_file)
print(enc_2tags)

pad_ids_train = padder(train_ids,input_len)
pad_type_ids_train = padder(train_type_ids,input_len)
pad_attention_mask_train = padder(train_attention_mask,input_len)
pad_tags_train = padder(encoded_tags_train, input_len)


pad_ids_val = padder(val_ids,input_len)
pad_type_ids_val = padder(val_type_ids,input_len)
pad_attention_mask_val = padder(val_attention_mask,input_len)
pad_tags_val = padder(encoded_tags_val, input_len)

preprocessor = hub.KerasLayer(encoder_url)
encoder = hub.KerasLayer(bert_url,trainable=True)

bert_ner_model = ner_model(num_tags)
bert_ner_model.compile(
    loss = tf.keras.losses.SparseCategoricalCrossentropy(),
    optimizer = tf.keras.optimizers.Adam(),
    metrics = ['accuracy']
)

bert_ner_model.fit(
    np.array(sentences_train),
    pad_tags_train,
    epochs = epochs,
    # batch_size = batch,
    )

# bert_ner_model.save_weights('drive/MyDrive/Colab Notebooks/trained_models/bert_ner_model/model_weights/bert_ner_weights.h5')

