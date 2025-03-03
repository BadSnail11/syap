import tensorflow as tf
from keras.src.datasets import imdb
from keras.src.models import Sequential
from keras.src.layers import SimpleRNN, Dense, Embedding
from keras.src import utils
from keras.src.utils.sequence_utils import pad_sequences

import numpy as np
import matplotlib.pyplot as plt

max_words = 10000

(x_train, )