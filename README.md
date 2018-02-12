# Image captioning with Attention

## About
This project was done as part of Statistical and machine learning course at Carnegie Mellon University. This repository describes an attention model that builds over basic image-text joint probability modelling approach for image captioning.

## Dataset

* Images - Flickr8k (Images: http://nlp.cs.illinois.edu/HockenmaierGroup/Framing_Image_Description/Flickr8k_Dataset.zip; Captions: http://nlp.cs.illinois.edu/HockenmaierGroup/Framing_Image_Description/Flickr8k_text.zip)
* Caption embeddings - GloVe embeddings (https://nlp.stanford.edu/projects/glove/)

## Model Archtechture

Include image

## Model Input

### Image 
Pre-trained 4096d VGGNET features. Run `vggnet.py` to obtain the image embeddings.

### Language 
GloVe embeddings 160d.  Run `caption/prepare_data.py` to obtain the word embeddings.

## Model Output

Next word in the caption

## Training

To train the models, run one of the train files below:

* Approach 1 : `train_model.py`
* ....

## Testing


## Results

Include image

## References



