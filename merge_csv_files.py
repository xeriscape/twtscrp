# -*- coding: utf-8 -*-

#Imports
import csv
import os
import hashlib
import glob
from time import gmtime, strftime

''' This file provides functionality to merge an arbitrary number of CSV files.
	Duplicate entires are removed. Currently, all of them have to be in the same directory, 
	all are merged, and there are no sanity checks. Those should probably be a thing. 
	
	#TODO: Parameters
	#TODO: Sanity checking
	#TODO: Todos
	'''
	
def scrub_row(line): #Make sure we're working in Unicode!
	scrub_result = []
	
	for l in line:
		r = l.decode('utf-8', errors='replace')
		n = r.encode('utf-8', errors='replace')
		
		scrub_result.append(n)
	
	return scrub_result


def main():
	#Some variables for later
	existing_entries = [] #List of MD5 hashes
	
	#Register default dialect (that's the one used by our very own websearch_scrape.py)
	csv.register_dialect('excel-two', delimiter=";", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar='"', quoting=csv.QUOTE_MINIMAL,skipinitialspace=True)
	
	#Get list of CSV files in current directory
	list_files = glob.glob('*.csv')
	
	#Set up output file & writer
	output_filename = "merge.csv"
	output_file = open(output_filename, 'ab')
	output_writer = csv.writer(output_file, dialect='excel-two')
	
	rows_written = 0
	rows_read = 0
	
	for lf in list_files:
		with open(lf, 'rb') as input_file:
			input_reader = csv.reader(input_file, dialect='excel-two')
			
			for current_row in input_reader:
				rows_read += 1 #Read in row
				
				#Make sure we're working in UTF-8
				current_row_utf8 = scrub_row(current_row)
				
				#Check for duplicates, write out row if it's found to not be one
				current_row_hash = hashlib.md5("".join(current_row_utf8)).hexdigest()
				if (current_row_hash not in existing_entries):
					existing_entries.append(current_row_hash)
					output_writer.writerow(current_row_utf8)
					rows_written += 1
					
				#Let the user now we're still live
				if (rows_read % 1234 == 0):
					print "{0}: Still working on {1}: {2} read, {3} written ...".format(strftime("%Y-%m-%d %H:%M:%S"), lf, rows_read, rows_written)
				
			print "\nDone with {0}: {1} lines read, {2} lines written\n".format(lf, rows_read, rows_written)
	

	return None
	

if __name__ == '__main__':
	main()
		
	