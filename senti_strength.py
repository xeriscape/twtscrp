# -*- coding: utf-8 -*-

''' Place this file in the same directory as your SentiStrengthCom.jar,
    your SentiStrength_Data folder and your CSV files to be analyzed. '''

import time
from time import sleep
import datetime
import glob
import csv
import shlex, subprocess
import re

import codecs

def replace_spc_error_handler(error):
# error is an UnicodeEncodeError/UnicodeDecodeError instance
# with these attributes:
# object = unicode object being encoded
# start:end = slice of object with error
# reason = error message
# Must return a tuple (replacement unicode object,
# index into object to continue encoding)
# or raise the same or another exception
	return (u' ' * (error.end-error.start), error.end)

def scrub_string(input_string):
	''' Force string into ASCII for analysis. '''
	codecs.register_error("replace_spc", replace_spc_error_handler) 
	to_scrub = input_string.decode('utf-8', errors='replace_spc')
	clean = to_scrub.encode('ascii', errors='replace_spc')
	return clean

def get_sentiment(sentiString, p, count):
	'''Take text, pass it to SentiStrengthCom.jar, compute sentiment. You can supply a pre-existing subprocess (p) e. g. if you want to use a nonstandard configuration. Note that it is strongly recommended to supply p even if you want to use the default configuration, as it makes very little sense to constantly close and re-open subprocesses. This function is partially based on the usage sample provided by Alec Larsen, University of the Witwatersrand, South Africa, 2012 (it's in the SentiStrength manual).'''
	#If no process is supplied, open a subprocess using shlex to get the command line string into the correct args list format. Note that supplying 

	#Communicate, via stdin, the string to be rated. Note that all spaces are replaced with +.
	sentiString = scrub_string(sentiString).replace(" ","+").replace("\n","+").replace("\t","+").replace("\r","+")
	p.stdin.write(sentiString)
	p.stdin.write("\n")

	#Read, via stdout, the results of the compotation.
	stdout_text = p.stdout.readline()
	p.stdout.flush()

	#Remove linebreaks and quotes to make later analysis easier.
	stdout_text = stdout_text.replace('"', '^')
	stdout_text = stdout_text.replace("\n", "")

	#As the results of the computation are tab-delimited, the result string needs to be split on \t.
	ret_val = stdout_text.split("\t")

	sleep(0.01) #This may seem arbitrary, but it helps SentiStrength not choke on the sheer volume

	#Returns (by default) positive, negative, neutral, explanation
	return ret_val


def main(tweets_file):
	#Set up default parameters for sentiment getting.
	#TODO: Have this input-dependent in some way...
	p = subprocess.Popen(shlex.split("java -jar SentiStrengthCom.jar sentenceCombineTot paragraphCombineTot trinary explain trinary negativeMultiplier 1 stdin sentidata ./SentiStrength_Data/"),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	#Set up a pattern for (very basic!) URL recognition (see below)
	url_pattern = re.compile("http(s)*:[^\s]+")

	#Check if tweets_file exists, prompt user for input if not

	#Prepare CSV boilerplate. Change this if your CSV setup does.
	csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)
	csv_headers = ["Author", "Tweet", "Date", "Hour", "Polarity_Pos", "Polarity_Neg", "Polarity_Neu", "Explanation"]

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
					try:
						tweet_text = None
						cur_time_float = None
						cur_time = None
						cur_hour = None

						if ((current_row[0] != "Username") and (len(current_row)==4)): #Skip the row with the CSV file headers, skip malformed rows
						
							#We "recycle" the process every 100 rows - this introduces overhead, but SentiStrength chokes up if sent too much data
							if ((rowcount % 100 ==0) or (p is None)):	
								if p is not None:
									p.communicate(None) #Close old process if one exists...
									sleep(0.1)
								#... then open a new one	
								p = subprocess.Popen(shlex.split("java -jar SentiStrengthCom.jar sentenceCombineTot paragraphCombineTot trinary explain trinary negativeMultiplier 1 stdin sentidata ./SentiStrength_Data/"),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, bufsize=1)

							#print "Doing",current_row
							
							#Username can be pretty much just grabbed
							user_name = current_row[0]
							
							#Force Tweet into ASCII and remove URLs (those confuse SentiStrength)
							tweet_text = scrub_string(current_row[3])

							#Strip URLs - those confuse SentiStrength as they contain dots, which are interpreted as sentence ends						
							tweet_text = re.sub(url_pattern, "<URL>", tweet_text)

							#Compute day of Tweet. Date & hour are stored seperately, as this enables easy computing of both hourly and daily scores.
							cur_time_float = (float(current_row[2]))
							cur_time = (datetime.datetime.utcfromtimestamp(cur_time_float/1000)).date()
							cur_hour = (datetime.datetime.utcfromtimestamp(cur_time_float/1000)).time().hour

							#Compute polarities of Tweet. Pad list if needed.
							cur_polarities = ["","","",""]
							cur_polarities = get_sentiment(tweet_text, p, rowcount)
							cur_polarities += [''] * (4 - len(cur_polarities))

							#The data has now been assembled and can be saved.
							output_writer.writerow([user_name, tweet_text.replace("\n", " "), cur_time, cur_hour, cur_polarities[0], cur_polarities[1], cur_polarities[2], cur_polarities[3].replace('\n', '').replace("\n", " ").replace("\r", " ") ])
				
							#Occasionally let user know we're still live
							rowcount += 1
							if (rowcount % 100 == 0): print "Rows processed: {0}".format(rowcount);
						else:
							print "Row skipped: ",current_row
					except Exception as e:
							print e
							print "Row skipped: ",current_row
	
	#We're done!
	print "Analysis complete."


if __name__ == '__main__':
	#TODO: Input path about here
	main("./")
