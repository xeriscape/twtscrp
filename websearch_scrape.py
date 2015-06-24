# -*- coding: utf-8 -*-

#Imports
import json
import urllib
import requests
import csv
import sys
from HTMLParser import HTMLParser
from lxml import html
import lxml
from time import gmtime, strftime
import time
import hashlib

#-------------------------------------------------------------------------------------------------
def get_search_chunk(query="", start_date="", end_date="", scroll_cursor="", is_realtime=True):
	'''This function takes a Twitter search query and some parameters as input, and returns the 
	   JSON data with which Twitter answers. Fields are (focused_refresh_interval, has_more_items,
	   is_refresh_request, is_scrolling_request, items_html, refresh_cursor, scroll cursor).

	   Refer to http://www.twitter.com/search for operators you can use in the query format.

	   Examples include:
	   * love OR hate		   * beer -root
	   * #haiku			       * from:alexiskold
	   * to:techcrunch   	   * @mashable
	   * near:NYC within:15mi  * since:2011-12-27
	   * until:2012-12-27	   * :)
	   * :(             	   * traffic ?
	   * filter:links   	   * lang:en
	   '''
	#Set up some variables to be used later
	r = None; data = None; success = False; add_twt = True;

	#If we want top results, not realtime results, we just leave off the "realtime" parameter
	if (is_realtime == True): realtime_text = "f=realtime&"
	else: realtime_text = ""	
	
	#Okay, assemble the query URL
	base_url = "https://twitter.com/i/search/timeline?{0}q={1} since:{2} until:{3}&include_available_features=1&include_entities=1&scroll_cursor={4}"
	query_url = base_url.format(realtime_text, query, start_date, end_date, scroll_cursor)

	#Do the actual search. TODO: Have this stuff configured by parameters of some sort
	success = False
	backoff = 1.0        #Total backoff time modifier 
	backoff_factor = 0.5 #How much the backoff increases each time
	sleeptime = 0.75     #Wait time in seconds
	max_sleep = 120      #When do we give up? (Default: When wait reaches 2 min)
	
	while not success: #Keep trying until the request goes through AND we get a useful items_html field
		wait_time = sleeptime*backoff
		time.sleep(wait_time) #Throttle requests a bit.
		r = None

		try: #The following two lines are what the function actually does: GET JSON data.
			r = requests.get(query_url)
			data = r.json()
			test_cursor = data["scroll_cursor"] #If scroll_cursor is missing from the data for some reason, this'll throw an exception
			
			if len(data["items_html"])>20: #Sometimes we'll accidentally get a blank items_html field. TODO: This could be more elegant...
				success = True
				add_twt = True
				backoff = 1.0
			else:
				#Are there more items but we didn't get them? Retry
				if( wait_time < max_sleep ):
					print "Error on {0}: items_html too short?".format(query_url)
					print "Retrying in {0} seconds".format(str(sleeptime*backoff))
					backoff = backoff * (1+backoff_factor)
					success = False
					
				#Are there no more items? Yeah, we're done
				else:
					success = True
					add_twt = False
					backoff = 1.0

		except (KeyboardInterrupt, SystemExit):
			print "Process aborted at {0}".format(query_url)
			raise #Always allow the process to be interrupted...

		except: #... but catch other exceptions (like timeouts) and just keep trying
			print "Error trying to retrieve {0}".format(query_url)
			print "Retrying in {0} seconds".format(str(sleeptime*backoff))
			backoff = backoff * (1+backoff_factor)
			if (wait_time < max_sleep): 
				success = False
			else:
				success = True
				add_twt = False
				backoff = 1.0

	#Once we've finally managed to extract the JSON data, return that
	return [add_twt, data]

#-------------------------------------------------------------------------------------------------
def extract_tweets(raw_html):
	''' This function scrapes the specified HTML string for Tweets and some related information.
	    Returns a list of lists(username, friendly_time, timestamp, tweet_text). '''
		
	if (len(raw_html)==0): raise TypeError("No raw_html specified");
		
	#Set up some temporary and holding variables for later
	retrieved_tweets = []; active_tweet= []; to_append="";

	#Query for username UNION time UNION timestamp UNION text
	xpath_query = "//span[starts-with(@class,'username')] | //small[@class = 'time']/a/@title | //span[starts-with(@class, '_timestamp')]/@data-time-ms | //p[contains(@class,'js-tweet-text')]"
	tree = html.fromstring(raw_html)
	query_results = tree.xpath(xpath_query)

	#Walk through query results
	for q in query_results:
		#We can extract all elements directly, EXCEPT for tweet text, because that's not an actual text element yet
		#See http://stackoverflow.com/questions/29398751 for why we query it like this (it's because of formatting)
		if (type(q) is lxml.html.HtmlElement):
			to_append = q.text_content()
		else: to_append = q;

		#Clean the extracted element up a little, make sure it's UTF-8 encoded and contains no linebreaks
		to_append = HTMLParser().unescape(to_append)
		to_append = to_append.encode('utf-8', errors='replace')
		to_append = to_append.replace('\n', ' ')

		#Append the cleaned-up string to the active element
		active_tweet.append(to_append)

		#Each tweet item contains (username, time, timestamp, text), so:
		#if we have reached a length of 4, the current item is finished and can be appended to the result set
		if (len(active_tweet) == 4):
			retrieved_tweets.append(active_tweet)
			active_tweet = []

	#Once we've walked through all query elements, the analysis is finished and we return the list-of-lists
	return retrieved_tweets

#-------------------------------------------------------------------------------------------------
def execute_search(query, since, until, crsor, is_realtime):
	''' Executing this file directly lets you do one of these searches with parameters you are asked to input.
	    Just hit Return if you don't want to specify them (that's actually possible). The filename is determined
		by the specified parameters. '''
		
	if (len(crsor) < 7): #Search cursors are absurdly long, so 
		crsor = "TWEET--" #Using this one fixes some issues with "blank" cursors	
	
	#Set up some variables for later
	next_cursor = crsor; success = False; tweet_count = 0;

	#Set up the output file and CSV writer. Search parameters are stored in a meta file.
	#TODO: There's probably a better way to do this. Deal w/ overly long file names.
	file_information = "This search for Tweets was started on {0}\n\n--Query: {1}\n--Since: {2}\n--Until: {3}\n--Cursor: {4}".format(strftime("%Y-%m-%d %H:%M:%S"), query, since, until, crsor)
	filename = "twts_"+hashlib.md5(file_information).hexdigest() #;D
	info_file_name = "{0}.meta".format(filename)
	
	with open(info_file_name, 'w') as f:
		f.write("Meta information for {0}\n\n".format(filename))
		f.write(file_information)
	
	filename = filename + ".csv"

	#Filter out some problematic characters (Windows dislikes them)
	filename = filename.replace(':','-'); filename = filename.replace('<','-');
	filename = filename.replace('/','-'); filename = filename.replace('>','-');
	filename = filename.replace('"','-'); filename = filename.replace("'",'-');
	filename = filename.replace('..',"-"); filename = filename.replace("|","-");
	filename = filename.replace("\\","-"); filename = filename.replace("?","-");
	
	#Open the CSV file, specify the dialect to be used, and write some column headers
	csvfile = open(filename, 'ab')
	csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)
	output_writer = csv.writer(csvfile, dialect='excel-two')
	csv_headers = ["Username","Time","Timestamp","Tweet"]
	output_writer.writerow(csv_headers)

	#Now for the actual data retrieval
	request_count = 0
	finished = False
	
	while not finished:
		#Let the user know we're still working...
		request_count = request_count + 1
		print "{0}: Now handling Tweet set {1}...".format(strftime("%Y-%m-%d %H:%M:%S"), request_count)
		with open(info_file_name, 'a') as f: f.write("{0}: Now handling Tweet set starting at cursor {1}...\n".format(strftime("%Y-%m-%d %H:%M:%S"), next_cursor));
		
		
		#Grab data
		search_chunk = get_search_chunk(query, since, until, next_cursor, is_realtime)
		
		#Check if we're done
		if( search_chunk[0] == True ): #If data exists, process it
			data = search_chunk[1]
		
			#Extract Tweets
			tweet_sets = extract_tweets(data["items_html"])

			#Write to disk
			for tweet_set in tweet_sets:
				output_writer.writerow(tweet_set)

			#Determine next page
			next_cursor = data["scroll_cursor"]
		
		#No more data means we're done
		else: # No more data means we're done
			print "\n\n{0}: No more items remaining.\n".format(strftime("%Y-%m-%d %H:%M:%S"))
			with open(info_file_name, 'a') as f: f.write("\n\n{0}: No more items remaining.\n".format(strftime("%Y-%m-%d %H:%M:%S")));
			finished = True
			continue
			
			
	print "\n{0}: Tweet retrieval for {1} finished successfully.".format(strftime("%Y-%m-%d %H:%M:%S"), filename)
#-------------------------------------------------------------------------------------------------
def main():
	#Do some inputting of search parameters. TODO: Validation
	query = raw_input("Query? (Example: sony lang:en)\n >   ")
	since = raw_input("Start date? (Example: 2011-04-15)\n >   ")
	until = raw_input("End date? (Example: 2011-05-25)\n >   ")
	crsor = raw_input("Start cursor? (Leave blank if none)\n >   ")
	
	execute_search(query, since, until, crsor, True)
#-------------------------------------------------------------------------------------------------


if __name__ == "__main__":
	''' The usual boilerplate... '''
	main()
