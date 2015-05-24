import websearch_scrape
from websearch_scrape import get_search_chunk, extract_tweets, execute_search
import glob, os
#------------------------------------------------------------------------------
def main():
	for search_file in glob.glob("*.srch"):
		try:
			x = open(search_file, "rb").readlines()
			query = x[0].replace("\n","").replace("\r","")
			since = x[1].replace("\n","").replace("\r","")
			until = x[2].replace("\n","").replace("\r","")
			crsor = x[3].replace("\n","").replace("\r","")
			is_realtime = True
		
			print "\n--------- Executing search ",x," ---------\n"
			websearch_scrape.execute_search(query, since, until, crsor, is_realtime)
			
		except (KeyboardInterrupt, SystemExit):
			print "Process aborted."
			raise
			
		except:
			print "Error at ", x

#------------------------------------------------------------------------------
if __name__ == "__main__":
	''' The usual boilerplate... '''
	main()