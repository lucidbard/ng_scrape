import urllib2, csv, unicodecsv, socket
from datetime import datetime
from bs4 import BeautifulSoup

# BATCH PROC
def ng_scrape_batch(start=0, finish=10):

	url_base = 'http://www.newgrounds.com/portal/view/'

	# Open the three files for writing:
	# file1 - normal.csv - scrape of regular movies & games
	# file2 - blammed.csv - scrape of blammed movies & games
	# file3 - count.txt - list of types
	# file4 - ng_scrape.log - log file of scraping activity

	# Open files and write headers
	# normal file
	f_normal = open('./output/normal.csv', 'a')
	normal_csvwriter = unicodecsv.UnicodeWriter(f_normal, delimiter=',')
	normal_header = ('id', 'title', 'author', 'date', 'time', 'content_type', 'size', 'category', 'views', 'stars', 'tags', 'author_comments')
	#normal_csvwriter.writerow(normal_header)
	# blammed file
	f_blammed = open('./output/blammed.csv', 'a')
	blammed_csvwriter = unicodecsv.UnicodeWriter(f_blammed, delimiter=',')
	blammed_header = ('id','title', 'author', 'date_uploaded', 'date_blammed', 'stars', 'author_comments')
	#blammed_csvwriter.writerow(blammed_header)
	# count and log file
	f_count = open('./output/count.txt', 'a')
	f_log = open('./output/ng_scrape.log', 'a')

	for i in range(start, finish):
		url = url_base + str(i)
	        print datetime.strftime(datetime.now(), '%m/%d/%Y %H:%M:%S') + ' Scraping ' + url
	        f_log.write(datetime.strftime(datetime.now(), '%m/%d/%Y %H:%M:%S') + ' Scraping ' + url + '\n')
 
		# soupify
		try:
			soup = soupify(url)                                           
		except:
			write_to_err(i)
	        	print('Error for ' + str(i))
	        	f_log.write('Error for ' + str(i) + '\n')
		else:	
			# Parse the soup title to determine page type                 
			title = soup.title
										      
			# Blammed page
			if soup.title.text[0:6] == 'Eulogy':
				output_text = ng_scrape_blammed(soup)                 
				output_text.insert(0, str(i))
				blammed_csvwriter.writerow(output_text)
				f_count.write(str(i) + ',' + 'blammed' + '\n')
				
			# 404	
			elif soup.title.text == 'Newgrounds - Error':
				f_count.write(str(i) + ',' + '404' + '\n')
			# Normal page
			else:                                                         
				try:
					output_text = ng_scrape_normal(soup) 
				except:
					write_to_err(i)
					print('Error for ' + str(i))
	        			f_log.write('Error for ' + str(i) + '\n')
				else:
					output_text.insert(0, str(i))
					normal_csvwriter.writerow(output_text)
					f_count.write(str(i) + ',' + 'normal' + '\n')

	f_log.close()
	f_count.close()
	f_blammed.close()
	f_normal.close()
	
# Write to error file
def write_to_err(i):
	f_err = open('./output/f_err.log', 'a')
	f_err.write(str(i) + '\n')
	f_err.close()
 
# MAIN PROC
def ng_scrape(url):

	# soupify
	soup = soupify(url)

	# Parse the soup title to determine page type
	title = soup.title
	output_text = '' 
	page_type = ''

	if soup.title.text[0:6] == 'Eulogy':
		output_text = ng_scrape_blammed(soup)
	elif soup.title.text == 'Newgrounds - Error':
		# skip iteration
		output_text = 'Page does not exist'
	else:
		output_text = ng_scrape_normal(soup) 

	return output_text

# CREATE SOUP
def soupify(url):

	# Open the request and create the soup
	req = urllib2.Request(url)
	response = urllib2.urlopen(req, timeout = 10.0)
	soup = BeautifulSoup(response.read())
	return soup

# BLAMMED SCRAPE
def ng_scrape_blammed(soup):

	# Scrape web page
	#url = ('http://www.newgrounds.com/portal/view/381115')
	
	
	# PARSE CONTENT
	# Page title
	title = soup.title.string.split(':')[1].strip()
	
	# Author
	author = soup.find_all("em")[5].text.split(' ')[2]

	# Author Comments
	try:
		author_comments = soup.find("h2", text="Author Comments").parent.findNextSibling().text
		author_comments = author_comments.replace('\n',' ').replace(',','').strip()
	except:
		author_comments = ''
	
	# Page Star Rating
	stars = soup.find(id='score_number').text
	
	# Date Uploaded
	date_uploaded = soup.find(id='eulogy').span.text.split(' ')[0]
	date_blammed = soup.find(id='eulogy').span.text.split(' ')[2]
	# Standard date formats
	date_uploaded = datetime.strftime(datetime.strptime(date_uploaded, '%m-%d-%y').date(), '%m/%d/%Y')
	date_blammed = datetime.strftime(datetime.strptime(date_blammed, '%m-%d-%y').date(), '%m/%d/%Y')
	
	return[title, author, date_uploaded, date_blammed, stars, author_comments]

# REGULAR SCRAPE
def ng_scrape_normal(soup):

	# Page title
	title = soup.title.string
	
	# Author
	author = soup.find_all('em')[4].text
	author = author.split(' ')[1]

	# Author Comments
	try:
		author_comments = soup.find("h2", text="Author Comments").parent.findNextSibling().text
		author_comments = author_comments.replace(',','').replace('\n',' ').strip()
	except:
		author_comments = ''
	
	# Page Star Rating
	#stars = soup.find(id='item_score').span.span.text # convert to text
	stars = soup.select('dd > span > span')[0].text
	
	# Number of Views
	views = soup.find('dt', text='Views:').findNextSibling().text
	views = views.split(' ')[0].replace(',','')
	
	# Date Uploaded
	date = soup.find('dt', text='Uploaded').findNextSibling().text
	time = date.split('|')[1].strip()
	date = date.split('|')[0].strip()
	# Convert date and time to standard formats
	date = datetime.strftime(datetime.strptime(date, '%b %d, %Y').date(), '%m/%d/%Y')
	time = datetime.strptime(time, '%I:%M %p %Z').time().strftime('%H:%M')
	
	# Category
	category = soup.find('dt', text='Genre:').findNextSibling('dd').text
	category = category.split(' - ')
	
	# Type
	content_type = soup.find('dt', text='File Info').findNextSibling().text.strip()

	# File Size
	size = soup.find('dt', text='File Info').findNextSibling().findNextSibling().text
	size = size.split()
	
	units = size[1]
	size = float(size[0].replace(',',''))
	
	# If kb covert to mb
	if units.lower() == 'kb':
		size /= 1000.0

	size = str(size)
	
	# Tags
	tag_html = soup.find('dt', text='Tags:').findNextSiblings('dd')
	tags = list()
	for tag in tag_html:
		tags.append(tag.text)
	
	return[title, author, date, time, content_type, size, ';'.join(category), views, stars, ';'.join(tags), author_comments]
