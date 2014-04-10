#!/usr/bin/env python
# 4/7/2014
# Charles O. Goddard

import sys
import numpy
import itertools
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import craigslist


def all_personals(city='boston'):
	generators = []
	for a in 'wm':
		for b in 'mw':
			print a+'4'+b
			generators.append((craigslist.postings(city, a+'4'+b), a+'4'+b))
	while True:
		for g, code in generators:
			posting = next(g)
			posting._title = posting._title + ' - ' + code
			yield posting


def main(city='boston', section='cas'):
	# Fetch a corpus of postings
	corpus = []
	for i, post in enumerate(all_personals()): #craigslist.postings(city, section)):
		corpus.append(post)
		if i >= 99: break

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
	sys.stdout.flush()

	vectorizer = TfidfVectorizer(stop_words='english')
	tfidf = vectorizer.fit_transform(documents)
	num_samples, num_features = tfidf.shape
	print '{0} samples, {1} features'.format(num_samples, num_features)

	matches = []

	for i, post in enumerate(corpus):
		try:
			candidates = [c for c in posts_gender[post.seeking] if (
				c.url != post.url and c.body != post.body and
				c.title != post.title and c.seeking in post.gender
			)]
		except KeyError:
			candidates = []
		if not candidates:
			continue

		dot_products = numpy.array([sum(tfidf[i].A[0] * tfidf[c.idx].A[0]) for c in candidates])
		idx = numpy.argmax(dot_products)
		score = dot_products[idx]
		if score > 0.8:
			print 'Suspiciously high score: {} {} -> {}'.format(score, post, candidates[idx])
			continue
		matches.append((dot_products[idx], post, candidates[idx]))

	matches.sort(reverse=True)

	print
	for i, (score, post, other) in enumerate(matches):
		print '{}. {}\n{}\n{}\n'.format(i + 1, score, post, other)
	print


if __name__ == '__main__':
	sys.exit(main())
