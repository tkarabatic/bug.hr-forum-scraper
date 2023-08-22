# Bug forum scraper

A simple app that enables scraping forum posts from the website of the _Bug_ magazine (_bug.hr_) and saving the data as plain text or CSV.

## **Usage examples**

Generate a list of subforums available from the main forum page:
> python bug.hr-forum-scraper --subforum-list
  
Generate a list of threads for page 5 of the DIY subforum:
> python bug.hr-forum-scraper -tl https://forum.bug.hr/forum/board/samogradnja-opcenito/39.aspx -pg 5

Scrape the posts for the first 10 pages of the specified thread and store the result in CSV format:
> python bug.hr-forum-scraper -pl https://forum.bug.hr/forum/topic/samogradnja-opcenito/raspberry-pi-projekti-ideje-savjeti/142032.aspx -pge 10 --csv
  
Generate a list of threads for all the pages of a subforum:
> python bug.hr-forum-scraper -tl https://forum.bug.hr/forum/board/it-trgovine/136.aspx -pge 999

Scrape all the posts for threads on the specified list, starting from the specified thread id (the threads before it will be skipped):
> python bug.hr-forum-scraper -plm bug_forum_sub_75_p1-210.txt -tid 170220

Scrape all the posts for threads on the specified list, store the result in both CSV and TXT formats, and use post ids in the resulting filenames (instead of page numbers):
> python bug.hr-forum-scraper -plm bug_forum_sub_75_p1-210.txt --txt-csv --plmpid

Same as above, but with initial page range and thread id specified (note: the page range only applies to the initial thread; all other threads will be scraped starting with page 1):
> python bug.hr-forum-scraper -plm bug_forum_sub_75_p1-210.txt --txt-csv --plmpid -tid 170220 -pg 500 -pge 600

Annotate select subforums for Sketch Engine upload (note: requires existing subforum folders populated with .csv thread files):
> python bug.hr-forum-scraper -as 40 138 75

Same as above, but increase the CSV field size limit to the system maximum (used to circumvent the 'field larger than field limit' error that can occur in the case of very large forum messages):
> python bug.hr-forum-scraper -as 40 138 75 --csv-field-max

