#!/usr/bin/env python
# 4/7/2014
# Charles O. Goddard

import sys
import numpy

import craigslist


def tokenize(text):
	chars = list(text)
	words = []
	word = []
	state = 0

	while chars:
		c = chars.pop(0)
		if state == 0:
			if c.isalnum() or c in "'-":
				state = 1
				word = [c]
		elif state == 1:
			if c.isalnum() or c in "'-":
				word.append(c.lower())
			else:
				state = 0
				words.append(''.join(word))

	return words


def termfreq(text):
	chunks = tokenize(text)
	freq = {}
	for word in chunks:
		if not word in freq:
			freq[word] = 0
		freq[word] += 1
	for word in freq:
		freq[word] /= float(len(chunks))
	return freq


def vectorize(text, word2idx):
	res = numpy.zeros(len(word2idx))
	freq = termfreq(text)
	for word in word2idx:
		res[word2idx[word]] = freq.get(word, 0)
	return res


def main(city='boston'):
	# Fetch a corpus of postings
	corpus = []
	for i, post in enumerate(craigslist.postings(city)):
		corpus.append(post)
		if i >= 49: break

	print 'Fetched', len(corpus), 'posts'

	all_text = '\n'.join(c.title + '\n' + c.body for c in corpus)

	freq = termfreq(all_text)
	words = sorted(((freq, word) for word, freq in freq.items()), reverse=True)

	print 'Top 15 most popular words:'
	for i in range(15):
		print '{0} ({1})'.format(words[i][1], words[i][0])

	word2idx = dict((word, idx) for idx, (freq, word) in enumerate(sorted(words, key=lambda (freq, word): -freq)))
	df = vectorize(all_text, word2idx)

	vectors = [vectorize(post.body, word2idx) / df for post in corpus]
	print vectors


if __name__ == '__main__':
	sys.exit(main())
