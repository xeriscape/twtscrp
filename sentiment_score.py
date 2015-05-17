# -*- coding: utf-8 -*-

import csv
#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
class SentimentDictionary():
	''' This class holds sentiment scores associated with various words. The sentiment_types that 
	    are considered can be defined (e. g. "positive, negative" or "anger, sadness, happiness")
		as well as (for each word) scores for some or all of those categories, allowing for a high
		degree of customization.
		
		sentiment_types:  Names for the different types of sentiments measured
		sentiment_scores: Dictionary of scores for words. 
						  Layout: Word,[emot_category:emot_score, emot_category:emot_score, ...]) '''

	sentiment_types  = [] 						  
	sentiment_scores = dict()
	
		
	def __init__(self, s_types): #Types ARE required, scores are NOT. TODO: Make 'em possible to define.
		self.sentiment_types = s_types #TODO: Make it possible to read in dictionaries from files?
		
		
		
	def add_word(self, word, scores):
		#Verify that word is not already placed
		if word in sentiment_scores:
			raise Error("Key {0} already exists.".format(word))
		
		add_scores=[]
		
		#If it isn't: Iterate through
		else:
			for (k, v in scores.items()):
				if (k not in self.sentiment_types): #Make sure all the sentiment types do exist
					raise Error("Sentiment type {0} does not exist in sentiment_types.".format(k))
					
				else:
					add_scores[k] = v
		
		#Once all sentiment types have been verified, add the item
		self.sentiment_scores[word] = k
					
			

#-------------------------------------------------------------------------------------------------
def compute_sentiment_score(text, sent_dict):
	''' Compute the sentiment scores of text, using the dictionary w/ values
	    specified by sent_dict. 
		
		text: The text to be analyzed.
		sent_dict: The SentimentDictionary to be used.
		Returns: An array containing the sentiment scores for each sentiment_type
		         used by the specified dictionary.
		'''
	
	sent_scores = []
	
	
	return
#-------------------------------------------------------------------------------------------------
def main():
	# Read in the name of a CSV file to be analyzed
	
	# Assume the meanings of the colums are like this:
	
	# Step through each CSV file and compute daily sentiment scores:
	
	# Write results to a separate CSV file:
#-------------------------------------------------------------------------------------------------
if __name__ == "__main__":
	''' The usual boilerplate... '''
	main()