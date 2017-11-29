

def prepare_dataset():
	token = 'Flickr8k_text/Flickr8k.token.txt'
	captions = open(token, 'r').read().strip().split('\n')

	d = {}
	for i, row in enumerate(captions):
		row = row.split('\t')
		row[0] = row[0][:len(row[0])-2]
		if row[0] in d:
			d[row[0]].append(row[1])
		else:
			d[row[0]] = [row[1]]

	images = 'Flickr8k_Dataset/Flicker8k_Dataset/'
	# Contains all the images
	img = glob.glob(images+'*.jpg')

	train_images_file = 'Flickr8k_text/Flickr_8k.trainImages.txt'
	train_images = set(open(train_images_file, 'r').read().strip().split('\n'))


if __name__ == '__main__':
	prepare_dataset()

