import websearch_scrape
from websearch_scrape import get_search_chunk, extract_tweets, execute_search
import glob, os
import datetime
#------------------------------------------------------------------------------
# Do a search for the week BEFORE a starting date. This is a bad solution to a 
# problem I should've foreseen - four days isn't nearly enough! - but I specialise
# in those, so here we are.


def main():
	for search_file in glob.glob("*.srch"):
		if 1==1:#try:
			x = open(search_file, "rb").readlines()
			query = x[0].replace("\n","").replace("\r","")
			since = x[1].replace("\n","").replace("\r","")
			crsor = x[3].replace("\n","").replace("\r","")
			is_realtime = True
			
			
			#srftime(format) method, to create a string representing the time under the control of an explicit format string
			#datetime.strptime() class method creates a datetime object from a string representing a date and time and a corresponding format string.
			
			since_to_date = datetime.datetime.strptime(since, "%Y-%m-%d")
			since_to_date = since_to_date - datetime.timedelta(days=7)
			
			new_since = since_to_date.strftime("%Y-%m-%d")
			
		
			print "\n--------- Executing search ",[query,new_since,since,crsor,is_realtime]," for ",x," ---------\n"
			#print " ",query,new_since,since, crsor,is_realtime
			websearch_scrape.execute_search(query, new_since,since, crsor, is_realtime)
			
		#except (KeyboardInterrupt, SystemExit):
		#	print "Process aborted."
		#	raise
			
		#except:
		#	print "Error at ", x

#------------------------------------------------------------------------------
if __name__ == "__main__":
	''' The usual boilerplate... '''
	main()