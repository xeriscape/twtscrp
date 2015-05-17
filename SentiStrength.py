# -*- coding: utf-8 -*-

''' Place this file in the same directory as your SentiStrengthCom.jar,
    your SentiStrength_Data folder and your CSV files to be analyzed. '''

import time
import datetime
import glob
import csv
import shlex, subprocess
import re

def getSentiment(sentiString, p):
	#Take text, compute sentiment. If you want to use a nonstandard configuration, supply a different p.
	#In general, supply p is strongly recommended so you don't keep re-starting processes.

	#Partial credit goes to Alec Larsen - University of the Witwatersrand, South Africa, 2012
	
	#open a subprocess using shlex to get the command line string into the correct args list format
	if p is None:	
		p = subprocess.Popen(shlex.split("java -jar SentiStrengthCom.jar trinary sentenceCombineTot explain stdin sentidata ./SentiStrength_Data/"),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	#communicate via stdin the string to be rated. Note that all spaces are replaced with +
	p.stdin.write(sentiString.replace(" ","+"))
	p.stdin.write("\n")
	stdout_text = p.stdout.readline()
	
	stdout_text = stdout_text.replace('"', '^')
	stdout_text = stdout_text.replace("\n", "")

	#Different values given are tab-separated
	ret_val = stdout_text.split("\t")

	#Returns (by default) positive, negative, neutral, explanation
	return ret_val


def main(tweets_file):
	#Set up default parameters for sentiment getting.
	#TODO: Have this input-dependent in some way...
	p = subprocess.Popen(shlex.split("java -jar ./SentiStrengthCom.jar trinary sentenceCombineTot explain stdin sentidata ./SentiStrength_Data/"),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	#Set up a pattern for (very basic!) URL recognition (see below)
	url_pattern = re.compile("http(s)*:[^\s]+")

	#Check if tweets_file exists, prompt user for input if not

	#Prepare CSV boilerplate. Change this if your CSV setup does.
	csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)
	csv_headers = ["Tweet", "Date", "Hour", "Polarity_Pos", "Polarity_Neg", "Polarity_Neu", "Explanation"]

	#Find a list of CSV files in the specified path...
	list_files = glob.glob('twts_*.csv')

	#For each file
	for lf in list_files:
		with open(lf, 'rb') as input_file:
			print "Now considering {0}".format(lf)
			#Set up output file: Open and write headers
			output_name = 'sents_{0}'.format(input_file.name)
			with open(output_name, 'ab') as output_file:
				output_writer = csv.writer(output_file, dialect='excel-two')
				output_writer.writerow(csv_headers)

				#Step through CSV file line by line
				rowcount = 0
				input_reader = csv.reader(input_file, dialect='excel-two')
				for current_row in input_reader:
					if (current_row[0] != "Username"): #Skip the row with the CSV file headers
						#Force Tweet into ASCII
						to_scrub  = current_row[3]
						to_scrub2 = to_scrub.decode('utf-8', errors='replace')
						tweet_text = to_scrub2.encode('ascii', errors='replace')

						#Strip URLs - those confuse SentiStrength as they contain dots, which are interpreted as sentence ends						
						tweet_text = re.sub(url_pattern, "<URL>", tweet_text)

						#Compute day of Tweet
						cur_time_float = (float(current_row[2]))
						cur_time = (datetime.datetime.utcfromtimestamp(cur_time_float/1000)).date()
						cur_hour = (datetime.datetime.utcfromtimestamp(cur_time_float/1000)).time().hour

						#Compute polarities of Tweet and pad list if needed
						cur_polarities = getSentiment(tweet_text, p)
						cur_polarities += [''] * (4 - len(cur_polarities))

						#Write output
						output_writer.writerow([tweet_text, cur_time, cur_hour, cur_polarities[0], cur_polarities[1], cur_polarities[2], cur_polarities[3].replace('\n', '') ])
				
						#Occasionally let user know we're still live
						rowcount += 1
						if (rowcount % 100 == 0): print "Rows processed: {0}".format(rowcount);
	
	#We're done!
	print "Analysis complete."


if __name__ == '__main__':
	#TODO: Input path about here
	main("./")
