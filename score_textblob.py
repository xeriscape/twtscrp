# -*- coding: utf-8 -*-

#Imports
from textblob import TextBlob
import glob
import csv
import unicode_literals

#Set up CSV stuff
csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)

#Look for .CSV files in current directory
list_files = glob.glob('*.csv')

#Step through them
for lf in list_files:
	with open(lf, 'rb') as input_file:
		input_reader = csv.reader(input_file, dialect='excel-two')
		
		for current_row in input_reader:
			tweet_text = unicode(current_row[3], 'utf-8')
			blob = TextBlob(tweet_text)
			for sentence in blob.sentences:
				print "Tweet: {0}\nScore: {1}\n\n".format(sentence, sentence.sentiment.polarity)