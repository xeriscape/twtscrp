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

#-------------------------------------------------------------------------------------------------
def get_search_chunk(query="", start_date="", end_date="", scroll_cursor="", is_realtime="True"):
	'''This function takes a Twitter search query and some parameters as input, and returns the 
	   JSON data with which Twitter answers. Fields are (focused_refresh_interval, has_more_items,
	   is_refresh_request, is_scrolling_request, items_html, refresh_cursor, scroll cursor).

	   Refer to http://www.twitter.com/search for operators you can use in the query format.'''
	#Set up some variables to be used later
	r = None; data = None; success = False;

	#If we want top results, not realtime results, we just leave off the "realtime" parameter
	if (is_realtime == True): realtime_text = "f=realtime&"
	else: realtime_text = ""	
	
	#Okay, assemble the query URL
	base_url = "https://twitter.com/i/search/timeline?{0}q={1} since:{2} until:{3}&include_available_features=1&include_entities=1&scroll_cursor={4}"
	query_url = base_url.format(realtime_text, query, start_date, end_date, scroll_cursor)

	#Do the actual search. TODO: Have this stuff configured by parameters of some sort
	success = False
	backoff = 1.0 
	backoff_factor = 0.5 #How much the backoff increases each time
	sleeptime = 0.75 #Wait time in seconds
	
	while not success: #Keep trying until the request goes through AND we get a useful items_html field
		time.sleep(sleeptime*backoff) #Throttle requests a bit. TODO: Parameter!
		r = None

		try: #The following two lines are what the function actually does: GET JSON data.
			r = requests.get(query_url)
			data = r.json()
			if len(data["items_html"])>20: #Sometimes we'll accidentally get a blank items_html field. TODO: This could be more elegant...
				success = True
				backoff = 1.0
			else:
				print "Error on {0}: items_html too short?".format(query_url)
				success = False

		except (KeyboardInterrupt, SystemExit):
			print "Process aborted at {0}".format(query_url)
			raise #Always allow the process to be interrupted...

		except: #... but catch other exceptions (like timeouts) and just keep trying
			print "Error trying to retrieve {0}".format(query_url)
			backoff = backoff * (1+backoff_factor)
			success = False

	#Once we've finally managed to extract the JSON data, return that
	return data

#-------------------------------------------------------------------------------------------------
def extract_tweets(raw_html=""):
	''' This function scrapes the specified HTML string for Tweets and some related information.
	    Returns a list of lists(username, friendly_time, timestamp, tweet_text). '''
	#Set up some temporary and holding variables for later
	retrieved_tweets = []; active_tweet= []; to_append="";

	#Query for username UNION time UNION timestamp UNION text
	xpath_query = "//span[starts-with(@class,'username')] | //small[@class = 'time']/a/@title | //span[starts-with(@class, '_timestamp')]/@data-time-ms | //p[starts-with(@class,'js-tweet-text')]"
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
def main():
	''' Executing this file directly lets you do one of these searches with parameters you are asked to input.
	    Just hit Return if you don't want to specify them (that's actually possible). The filename is determined
		by the specified parameters. '''
	#Set up some variables for later
	next_cursor = ""; success = False; tweet_count = 0;

	#Do some inputting of search parameters. TODO: Validation
	query = raw_input("Query?\n >   ")
	since = raw_input("Start date (YYYY-MM-DD)?\n >   ")
	until = raw_input("End date (YYYY-MM-DD)?\n >   ")
	crsor = raw_input("Start cursor? (Leave blank if none)\n >   ")

	if (len(crsor)>0): #Cursors CAN be specified if that is wanted
		next_cursor = crsor

	#Set up the output file and CSV writer
	filename = "tweets"
	if (len(query)>0): filename = filename+"_"+query;
	if (len(since)>0): filename = filename+"_from "+since;
	if (len(until)>0): filename = filename+"_until "+until;
	if (len(crsor)>0): filename = filename+"_starting"; #TODO: Deal with overly long file names
	filename = filename + ".csv"

	#Filter out some problematic characters (Windows dislikes them)
	filename = filename.replace(':','-'); filename = filename.replace('<','-');
	filename = filename.replace('/','-'); filename = filename.replace('>','-');
	filename = filename.replace('"','-'); filename = filename.replace("'",'-');
	filename = filename.replace('..',"-"); filename = filename.replace("|","-");
	filename = filename.replace("\\","-"); filename = filename.replace("?","-");
	
	#Open the CSV file, specify the dialect to be used, and write some column headers
	csvfile = open(filename, 'a')
	csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)
	output_writer = csv.writer(csvfile, dialect='excel-two')
	csv_headers = ["Username","Time","Timestamp","Tweet"]
	output_writer.writerow(csv_headers)

	#Now for the actual data retrieval
	request_count = 0
	while True: #TODO: End a little more graciously than that :(
		#Let the user know we're still working...
		request_count = request_count + 1
		print "{0}: Now handling Tweet set {1}...".format(strftime("%Y-%m-%d %H:%M:%S"), request_count)

		#Grab data
		data = get_search_chunk(query, since, until, next_cursor, True)

		#Extract Tweets
		tweet_sets = extract_tweets(data["items_html"])

		#Write to disk
		for tweet_set in tweet_sets:
			output_writer.writerow(tweet_set)

		#Determine next page
		next_cursor = data["scroll_cursor"]
#-------------------------------------------------------------------------------------------------
if __name__ == "__main__":
	''' The usual boilerplate... '''
	main()
