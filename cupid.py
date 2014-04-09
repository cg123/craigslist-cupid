#!/usr/bin/env python
# 4/7/2014
# Charles O. Goddard

import sys
import numpy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import craigslist


def main(city='boston'):
	# Fetch a corpus of postings
	corpus = []
	for i, post in enumerate(craigslist.postings(city)):
		corpus.append(post)
		if i >= 49: break

	print 'Fetched', len(corpus), 'posts'

	documents = [c.title + '\n' + c.body for c in corpus]
	print 'Got all text'

	vectorizer = CountVectorizer(stop_words='english')
	X = vectorizer.fit_transform(documents)
	num_samples, num_features = X.shape
	print '{0} samples, {1} features'.format(num_samples, num_features)
	print vectorizer.get_feature_names()
	print(X)


if __name__ == '__main__':
	sys.exit(main())
