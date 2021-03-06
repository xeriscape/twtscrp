# Scraping and sentiment detection utilities for Twitter analysis
## Explanation of purpose
* Social media analysis requires large amounts of data, often retrieved from social networks such as Twitter.
* Twitter provides a search API, but this API only goes one week into the past. At the same time, the web search can retrieve older messages.
* This repository contains a set of tools that allow the user to send queries to the web search API, to store Tweets and basic meta-data locally, and to conduct sentiment analysis on the stored Tweets.
* It is strongly recommended to use analysis tools that can cope with the special properties of the "social media dialect" spoken on Twitter, such as SentiStrength. As the Java version of SentiStrength is not publically available, a significantly more basic alternative is also included.

## Usage (single search)
* Run websearch_scrape.py to execute a search for Tweets and to save them (with some meta-information) in a CSV file. Refer to http://www.twitter.com/search for operators you can use. As this search scrapes Twitter's web search and does not use the search API, it is able to retrieve Tweets that are older than a week. In case you want to interrupt and later resume a search, you can specify a search cursor (check the .meta file to see the search cursors that are being / have been processed).
* Run merge_csv_files.py to merge all CSV files in the current directory. This tool is a very blunt instrument that should really only be used if you had to split up a search and now want to merge the files. Note that duplicates are automatically removed and that entries are forced into UTF-8 format. You can probably use UNIX tools instead of this utility, but it's provided for completeness' sake.
* Run senti_strength.py to analyse the retrieved Tweets and to compute sentiment scores. Note that the JAR file ("SentiStrengthCom.jar") MUST be in the same folder as the script, as MUST the SentiStrength_Data directory. The output is stored in another CSV file.
* Alternatively, Tweets can be analyzed using score_textblob.py. This method is significantly more primitive, but it also does not require the presence of the SentiStrengthCom.jar file and can in fact be used completely standalone.

## Usage (batch search)
* Create one or several files containing your search terms. The layout for these files is "searchterm\nstartdate\nenddate\nstartcursor" and they must have the file extension ".srch".
* Run automate_search.py to execute all the searches (.srch files) in the current directory.
* Run senti_strength.py or score_textblob.py to analyse the retrieved Tweets and to compute sentiment scores.