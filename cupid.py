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
		if i >= 499: break

	print 'Fetched', len(corpus), 'posts'

	# Categorize posts by gender
	posts_gender = {}
	for i, post in enumerate(corpus):
		post.idx = i
		code = post.title.split(' - ')[-1]
		try:
			gender, seeking = code.split('4')
		except ValueError:
			print code
			post.gender = '??'
			post.seeking = '??'
			continue
		post.gender = gender
		post.seeking = seeking

		if not gender in posts_gender:
			posts_gender[gender] = []
		posts_gender[gender].append(post)

	documents = [c.title + '\n' + c.body for c in corpus]
	print 'Got all text'

	vectorizer = TfidfVectorizer(stop_words='english')
	tfidf = vectorizer.fit_transform(documents)
	print
	print tfidf[0].A[0]
	print
	num_samples, num_features = tfidf.shape
	print '{0} samples, {1} features'.format(num_samples, num_features)
	print vectorizer.get_feature_names()
	print

	# similarities =  (X * X.T).A - numpy.eye(len(corpus))
	# for i, post in enumerate(corpus):
	# 	other_idx = numpy.argmax(similarities[i])
	# 	other_post = corpus[other_idx]
	# 	print str(post), '->', str(other_post)

	for i, post in enumerate(corpus):
		try:
			candidates = [c for c in posts_gender[post.seeking] if c.idx != i and c.seeking in post.gender]
		except KeyError:
			candidates = []
		if not candidates:
			print str(post), '-> shit out of luck'
			continue

		dot_products = numpy.array([sum(tfidf[i].A[0] * tfidf[c.idx].A[0]) for c in candidates])
		idx = numpy.argmax(dot_products)
		print str(post), '->', str(candidates[idx])


if __name__ == '__main__':
	sys.exit(main())
