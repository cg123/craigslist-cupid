# 4/9/2014
# Charles O. Goddard
"""
craigslist: Functions for scraping Craigslist postings.
"""

import dateutil.parser
import unicodedata
import requests
import bs4


def sanitize(text):
	return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')


class Posting(object):
	"""
	A posting on craigslist.
	"""
	def __init__(self, url, title=None):
		self.url = url
		self._title = sanitize(title).strip()
		self._body = None
		self._posted = None
		self.id = int(url.split('/')[-1].split('.')[0])

	def fetch_details(self):
		"""
		Fetch posting details (title, body text) from Craigslist.
		"""
		# Make HTTP request
		r = requests.get(self.url)
		if r.status_code != 200:
			return False

		# Parse returned HTML
		soup = bs4.BeautifulSoup(r.text, 'html5lib')

		if not soup.title.string:
			# Post has been deleted
			self._body = '<DELETED>'
			self._posted = -1
			return False

		self._title = sanitize(soup.title.string).strip()

		postingbody = soup.find('section', id='postingbody')
		if postingbody:
			try:
				self._body = ' '.join([sanitize(unicode(x)) for x in postingbody.contents]).replace('<br/>','\n').strip()
			except UnicodeEncodeError, e:
				print self.url
				print postingbody
				raise
		else:
			self._body = None

		posted = soup.time.get('datetime')
		self._posted = dateutil.parser.parse(posted)

		return True

	@property
	def title(self):
		if self._title is None:
			self.fetch_details()
		return self._title

	@property
	def body(self):
		if self._body is None:
			self.fetch_details()
		return self._body

	@property
	def posted(self):
		if self._posted is None:
			self.fetch_details()
		return self._posted

	def __repr__(self):
		return '{!s}({!r})'.format(type(self).__name__, self.url)

	def __str__(self):
		return '{} ({})'.format(self.title, self.url)


def postings(location='boston', section='cas'):
	'''
	List all craigslist postings for a given location and section.

	Returns a generator yielding (url, title) pairs.
	'''
	base_url = 'http://{0}.craigslist.org'.format(location)
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
			yield Posting(url, a.string)

		idx += 1

