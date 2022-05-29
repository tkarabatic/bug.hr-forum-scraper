# Bug forum scraper

A simple app that enables scraping forum posts from the website of the _Bug_ magazine (_bug.hr_) and saving the data as plain text or CSV.

## **Usage examples**

  Generate a list of subforums available from the main forum page and override the default filename base:

    python bug.hr-forum-scraper --subforum-list -fn my-filename
  
  Generate a list of threads for page 5 of the DIY subforum:

    python bug.hr-forum-scraper -tl https://forum.bug.hr/forum/board/samogradnja-opcenito/39.aspx -pg 5

  Scrape the posts for the first 10 pages of the specified thread and store the result in CSV format:

    python bug.hr-forum-scraper -pl https://forum.bug.hr/forum/topic/samogradnja-opcenito/raspberry-pi-projekti-ideje-savjeti/142032.aspx -pge 10 --csv
