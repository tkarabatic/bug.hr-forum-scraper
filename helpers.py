from bs4 import BeautifulSoup
import re
from utils import clean_string, get_date_string, get_resource_id, get_response

ROOT_URL = 'https://forum.bug.hr'
ANCHOR_PATH = 'a.naslov'
POST_PATH = 'div.post'
POST_CLASS_QUOTE = 'editor_quote'
POST_CLASS_MAIN = 'postOn'
POST_CLASS_DATE = 'datum'
POST_CLASS_CONTENT = 'porukabody'


def get_paginated_url(url, page=1):
  """
  Note: The forum.bug.hr 'page' URL param appears to be zero-indexed, and is
  only included for non-zero values (there will be no results for 'page=0').
  Example: to fetch the first page, the 'page' param is not included. To fetch
  the second page, the 'page' param is 1, and so on.
  """
  if (page < 2):
    return url
  return '%s?page=%s' % (url.split('?')[0], page - 1)


def get_post_data(bs4_tag):
  post_classes = [POST_CLASS_MAIN, POST_CLASS_DATE, POST_CLASS_CONTENT]
  divs = bs4_tag.find_all('div', attrs={'class': post_classes })
  post_id = divs[0]['id'].split('post')[1]
  post_date = get_date_string(divs[1].text)
  post_content = divs[2].text
  return (post_id, post_date, post_content)


def get_thread_post(bs4_tag, is_csv=False):
  if not is_csv:
    content = bs4_tag.find('div', {'class': POST_CLASS_CONTENT})
    return clean_string(content.text)
  data = get_post_data(bs4_tag)
  return ','.join([data[0], data[1], '"%s"' % clean_string(data[2], is_csv)])


def get_thread_posts(thread_url, pages, is_csv=False):
  post_list = []
  for page in pages:
    response = get_response(get_paginated_url(thread_url, page))
    soup = BeautifulSoup(response.content, 'html.parser')
    # remove embedded quotes
    for div in soup.find_all('div', {'class': POST_CLASS_QUOTE}):
      div.decompose()
    posts = list(map(lambda x: get_thread_post(x, is_csv), soup.select(POST_PATH)))
    post_list += posts
  return post_list


def get_link(bs4_tag, is_csv=False):
  url = '%s%s' % (ROOT_URL, bs4_tag['href'])
  if not is_csv:
    return url
  return ','.join([str(get_resource_id(url)), url])


def get_link_list(url, pages, is_csv=False):
  link_list = []
  for page in pages:
    response = get_response(get_paginated_url(url, page))
    # 'html.parser' is recommended over parsing 'res.text' to avoid character
    # encoding issues
    soup = BeautifulSoup(response.content, 'html.parser')
    links = list(map(lambda x: get_link(x, is_csv), soup.select(ANCHOR_PATH)))
    link_list += links
  return link_list