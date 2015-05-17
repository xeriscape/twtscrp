# -*- coding: utf-8 -*-

#Imports
import textblob
from textblob import TextBlob
import glob
import csv
import time
import datetime

#Set up CSV stuff
csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)

#Look for .CSV files in current directory
list_files = glob.glob('twts_*.csv')

#Prepare output facilities
csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)
csv_headers = ["Tweet", "Date", "Hour", "Polarity"]

#Step through them
rowcount = 0
for lf in list_files:
	with open(lf, 'rb') as input_file:
		output_name = 'tbsents_{0}'.format(input_file.name)
		input_reader = csv.reader(input_file, dialect='excel-two')
		
		with open(output_name, 'ab') as output_file:
			output_writer = csv.writer(output_file, dialect='excel-two')
			output_writer.writerow(csv_headers)
		
			for current_row in input_reader:
				if "Username" in current_row: continue; #Skip the row with the headers
				#Input headers: ["Username","Time","Timestamp","Tweet"]
				#Output headers: ["Tweet", "Date", "Hour", "Polarity"]
			
				#Compute day of Tweet
				cur_time_float = float((current_row[2])) * 1.0
				cur_time = (datetime.datetime.utcfromtimestamp(cur_time_float/1000)).date()
				cur_hour = (datetime.datetime.utcfromtimestamp(cur_time_float/1000)).time().hour
			
				#Un-sentencify Tweet
				tweet_text = unicode(current_row[3], 'utf-8').replace(".", "~").encode('ascii', errors='replace') + "."
				
				#Compute sentiment & write out
				blob = TextBlob(tweet_text)
				sentence = blob.sentences[0]
				output_writer.writerow([tweet_text, cur_time, cur_hour, sentence.sentiment.polarity] )
				
				#Occasionally let user know we're still live
				rowcount += 1
				if (rowcount % 100 == 0): print "Rows processed: {0}".format(rowcount);