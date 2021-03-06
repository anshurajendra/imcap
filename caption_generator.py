from vgg16 import VGG16
from keras.applications import inception_v3
import numpy as np
import pandas as pd
from keras.models import *
from keras.layers import LSTM, Embedding, TimeDistributed, Dense, RepeatVector, Merge, Activation, Flatten, Input
from keras.preprocessing import image, sequence
from keras.callbacks import ModelCheckpoint
import cPickle as pickle
from keras.layers import merge
from keras.layers.core import *

EMBEDDING_DIM = 128
SINGLE_ATTENTION_VECTOR = False


class CaptionGenerator():

    def __init__(self):
        self.max_cap_len = None
        self.vocab_size = None
        self.index_word = None
        self.word_index = None
        self.total_samples = None
        self.encoded_images = pickle.load( open( "encoded_images.p", "rb" ) )
        self.encoded_vocab = pickle.load( open( "encoded_vocab.p", "rb" ) )
        self.variable_initializer()

    def variable_initializer(self):
        df = pd.read_csv('Flickr8k_text/flickr_8k_train_dataset.txt', delimiter='\t')
        nb_samples = df.shape[0]
        iter = df.iterrows()
        caps = []
        for i in range(nb_samples):
            x = iter.next()
            caps.append(x[1][1])

        self.total_samples=0
        for text in caps:
            self.total_samples+=len(text.split())-1
        print "Total samples : "+str(self.total_samples)
        
        words = [txt.split() for txt in caps]
        unique = []
        for word in words:
            unique.extend(word)

        unique = list(set(unique))
        self.vocab_size = len(unique)
        self.word_index = {}
        self.index_word = {}
        for i, word in enumerate(unique):
            self.word_index[word]=i
            self.index_word[i]=word

        max_len = 0
        for caption in caps:
            if(len(caption.split()) > max_len):
                max_len = len(caption.split())
        self.max_cap_len = max_len
        print "Vocabulary size: "+str(self.vocab_size)
        print "Maximum caption length: "+str(self.max_cap_len)
        print "Variables initialization done!"


    def data_generator(self, batch_size = 32):
        partial_caps = []
        next_words = []
        images = []
        print "Generating data..."
        gen_count = 0
        df = pd.read_csv('Flickr8k_text/flickr_8k_train_dataset.txt', delimiter='\t')
        nb_samples = df.shape[0]
        iter = df.iterrows()
        caps = []
        imgs = []
        for i in range(nb_samples):
            x = iter.next()
            caps.append(x[1][1])
            imgs.append(x[1][0])


        total_count = 0
        while 1:
            image_counter = -1
            for text in caps:
                image_counter+=1
                current_image = self.encoded_images[imgs[image_counter]]
                for i in range(len(text.split())-1):
                    total_count+=1
                    partial = [self.word_index[txt] for txt in text.split()[:i+1]]
                    partial_enc = [self.encoded_vocab[txt] for txt in text.split()[:i+1]]
                    partial_capv= np.zeros((self.max_cap_len, 200))
                    partial_capv[:i+1,:]=partial_enc
                    partial_caps.append(partial_capv)
                    next = np.zeros(self.vocab_size)
                    next[self.word_index[text.split()[i+1]]] = 1
                    next_words.append(next)
                    images.append(current_image)

                    if total_count>=batch_size:
                        next_words = np.asarray(next_words)
                        partial_caps = np.asarray(partial_caps)
                        images = np.asarray(images)
                        #partial_caps = sequence.pad_sequences(partial_caps, maxlen=self.max_cap_len, padding='post')
                        total_count = 0
                        gen_count+=1
                        print "yielding count: "+str(gen_count)
                        yield [[images, partial_caps], next_words]
                        partial_caps = []
                        next_words = []
                        images = []
        
    def load_image(self, path):
        img = image.load_img(path, target_size=(224,224))
        x = image.img_to_array(img)
        return np.asarray(x)

    def attention_3d_block(self, inputs):
        # inputs.shape = (batch_size, time_steps, input_dim)
        input_dim = int(inputs.shape[2])
        a = Permute((2, 1))(inputs)
        a = Reshape((input_dim, self.max_cap_len))(a) # this line is not useful. It's just to know which dimension is what.
        a = Dense(self.max_cap_len, activation='softmax')(a)
        if SINGLE_ATTENTION_VECTOR:
            a = Lambda(lambda x: K.mean(x, axis=1), name='dim_reduction')(a)
            a = RepeatVector(input_dim)(a)
        a_probs = Permute((2, 1), name='attention_vec')(a)
        output_attention_mul = merge([inputs, a_probs], name='attention_mul', mode='mul')
        return output_attention_mul


    def create_model(self, ret_model = False):
        #base_model = VGG16(weights='imagenet', include_top=False, input_shape = (224, 224, 3))
        #base_model.trainable=False
        image_model = Sequential()
        #image_model.add(base_model)
        #image_model.add(Flatten())
        image_model.add(Dense(EMBEDDING_DIM, input_dim = 4096, activation='relu'))
        image_model.add(RepeatVector(self.max_cap_len))

        lang_model = Sequential()
        lang_model.add(Dense(EMBEDDING_DIM, input_shape=(self.max_cap_len, 200)))
        lang_model.add(TimeDistributed(Dense(EMBEDDING_DIM)))

        model = Sequential()
        model.add(Merge([image_model, lang_model], mode='concat'))
        model.add(LSTM(1000,return_sequences=False))
        model.add(Dense(self.vocab_size))
        model.add(Activation('softmax'))
        model.summary()

        print "Model created!"

        if(ret_model==True):
            return model

        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        return model
    def create_basic_model(self, ret_model = False):
        #base_model = VGG16(weights='imagenet', include_top=False, input_shape = (224, 224, 3))
        #base_model.trainable=False
        image_model = Sequential()
        #image_model.add(base_model)
        #image_model.add(Flatten())
        image_model.add(Dense(EMBEDDING_DIM, input_dim = 4096, activation='relu'))
        image_model.add(RepeatVector(self.max_len))

        lang_model = Sequential()
        lang_model.add(Dense(EMBEDDING_DIM, input_shape=(self.max_len,200)))
        lang_model.add(TimeDistributed(Dense(EMBEDDING_DIM)))

        model = Sequential()
        model.add(Merge([image_model, lang_model], mode='concat'))
        model.add(RNN(1000,return_sequences=False))
        model.add(Dense(self.vocab_size))
        model.add(Activation('softmax'))
        model.summary()

        print "Basic Model created!"

        if(ret_model==True):
            return model

        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        return model

    def create_advanced_model(self, ret_model = False):
        #base_model = VGG16(weights='imagenet', include_top=False, input_shape = (224, 224, 3))
        #base_model.trainable=False
        image_model = Sequential()
        #image_model.add(base_model)
        #image_model.add(Flatten())
        image_model.add(Dense(EMBEDDING_DIM, input_dim = 4096, activation='relu'))
        image_model.add(RepeatVector(20))

        lang_model = Sequential()
        lang_model.add(Dense(EMBEDDING_DIM, input_shape=(20,200)))
        lang_model.add(TimeDistributed(Dense(EMBEDDING_DIM)))

        model = Sequential()
        model.add(Merge([image_model, lang_model], mode='concat'))
        model.add(RNN(1000,return_sequences=False))
        model.add(Dense(self.vocab_size))
        model.add(Activation('softmax'))
        model.summary()

        print "Basic Model created!"

        if(ret_model==True):
            return model

        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        return model

    def create_advanced_att_model_after(self, ret_model = False):
        image_model = Sequential()
        #image_model.add(base_model)
        #image_model.add(Flatten())
        image_model.add(Dense(EMBEDDING_DIM, input_dim = 4096, activation='relu'))

        image_model.add(RepeatVector(self.max_cap_len))

        inputs = Input(shape=(self.max_cap_len,200))
        embedded = Dense(EMBEDDING_DIM, input_shape = (self.max_cap_len,200))(inputs)
        lstm_out = LSTM(EMBEDDING_DIM, return_sequences=True)(embedded)
        attention_mul = self.attention_3d_block(lstm_out)
        #attention_mul = Flatten()(attention_mul)
        outputs = TimeDistributed(Dense(EMBEDDING_DIM))(attention_mul)
        lang_model = Model(input=[inputs], output=outputs)

        model = Sequential()
        model.add(Merge([image_model, lang_model], mode='concat'))
        model.add(LSTM(1000,return_sequences=False))
        model.add(Dense(self.vocab_size))
        model.add(Activation('softmax'))
        model.summary()

        print "Model created!"

        if(ret_model==True):
            return model

        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        return model

    def create_advanced_att_model_before(self, ret_model = False):
        image_model = Sequential()
        #image_model.add(base_model)
        #image_model.add(Flatten())
        image_model.add(Dense(EMBEDDING_DIM, input_dim = 4096, activation='relu'))

        image_model.add(RepeatVector(self.max_cap_len))

        inputs = Input(shape=(self.max_cap_len,200))
        embedded = Dense(EMBEDDING_DIM, input_shape = (self.max_cap_len,200))(inputs)
        attention_mul = self.attention_3d_block(embedded)
        attention_mul = LSTM(EMBEDDING_DIM, return_sequences=False)(attention_mul)
        dense = Dense(EMBEDDING_DIM)(attention_mul)
        outputs = RepeatVector(self.max_cap_len)(dense)
        outputs = TimeDistributed(Dense(EMBEDDING_DIM))(outputs)
        lang_model = Model(input=[inputs], output=outputs)

        model = Sequential()
        model.add(Merge([image_model, lang_model], mode='concat'))
        model.add(LSTM(1000,return_sequences=False))
        model.add(Dense(self.vocab_size))
        model.add(Activation('softmax'))
        model.summary()

        print "Model created!"

        if(ret_model==True):
            return model

        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        return model

    def get_word(self,index):
        return self.index_word[index]