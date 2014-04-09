#!/usr/bin/env python
# 4/7/2014
# Charles O. Goddard

import sys

import requests
import numpy
import bs4


def postings(city='boston', section='cas'):
	'''
	List all craigslist postings for a given city and section.

	Returns a generator yielding (url, title) pairs.
	'''
	base_url = 'http://{0}.craigslist.org/'.format(city)
	idx = 0
	while True:
		# Get next hundred postings
		url = '{0}/{1}/index{2:03}.html'.format(base_url, section, idx * 100)
		r = requests.get(url)
		if r.status_code != 200:
			raise ValueError(r.status_code)

		# Parse HTML
		soup = bs4.BeautifulSoup(r.text, 'html5lib')

		# Find and yield postings
		for span in soup.find_all('span', 'pl'):
			a = span.a
			url = a.get('href')
			if not url.startswith(base_url):
				url = base_url + url
			yield url, a.string

		idx += 1


def fetch_post(url):
	r = requests.get(url)
	if r.status_code != 200:
		raise ValueError(r.status_code)
	soup = bs4.BeautifulSoup(r.text, 'lxml')
	body = soup.find('section', id='postingbody')
	for section in soup.find_all('section'):
		if section.get('id') == 'postingbody':
			return '\n'.join(map(str, section.contents)).replace('<br/>','\n')

	print '!!', url
	for section in soup.find_all('section'):
		print section.get('id')
		print '!'*64
		print
	print 'done'
	return ''


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
	for i, (url, title) in enumerate(postings(city)):
		body = fetch_post(url)
		if not title:
			print '!!! no title -', title, url
		elif not body:
			print '!!! no body -', title, url
		else:
			corpus.append(title + '\n' + body)
		if i >= 49: break

	print 'Fetched', len(corpus), 'posts'

	freq = termfreq('\n'.join(corpus))
	words = sorted(((freq, word) for word, freq in freq.items()), reverse=True)

	print 'Top 15 most popular words:'
	for i in range(15):
		print '{0} ({1})'.format(words[i][1], words[i][0])

	word2idx = dict((word, idx) for idx, (freq, word) in enumerate(words))
	df = vectorize('\n'.join(corpus), word2idx)

	vectors = [vectorize(post, word2idx) / df for post in corpus]
	print vectors


if __name__ == '__main__':
	sys.exit(main())
