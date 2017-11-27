import numpy as np
import cPickle as pickle

GLOVE_DIR = 'glove'

embeddings_index = {}
f = open(os.path.join(GLOVE_DIR, 'glove.6B.200d.txt'))
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

print('Found %s word vectors.' % len(embeddings_index))

with open( "encoded_vocab.p", "wb" ) as pickle_f:
	pickle.dump(embeddings_index, pickle_f)  