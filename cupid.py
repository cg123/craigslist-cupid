#!/usr/bin/env python
# 4/7/2014
# Charles O. Goddard

import sys

import requests
import bs4


def postings(city='boston', section='cas'):
	'''
	List all craigslist postings for a given city and section.

	Returns a generator yielding (url, title) pairs.
	'''
	idx = 0
	while True:
		# Get next hundred postings
		url = 'http://{0}.craigslist.org/{1}/index{2:03}.html'.format(city, section, idx * 100)
		print(url)
		r = requests.get(url)
		if r.status_code != 200:
			raise ValueError(r.status_code)

		# Parse HTML
		soup = bs4.BeautifulSoup(r.text, 'html5lib')

		for span in soup.find_all('span', 'pl'):
			a = span.a
			yield a.get('href'), a.string

		idx += 1


def main(city='boston'):
	for i, url in enumerate(postings()):
		print url
		if i > 10:
			break
	return 0


if __name__ == '__main__':
	sys.exit(main())
