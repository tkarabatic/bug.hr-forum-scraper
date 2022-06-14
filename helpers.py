from constants import (
  ANCHOR_PATH, POST_CLASS_CODE, POST_CLASS_CONTENT, POST_CLASS_DATE,
  POST_CLASS_IMAGE, POST_CLASS_MAIN, POST_CLASS_QUOTE, POST_PATH, ROOT_URL
)
import re
from utils import clean_string, get_date_string, get_resource_id, get_response


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
  post_id = str(divs[0]['id'].split('post')[1])
  post_date = get_date_string(divs[1].text)
  post_content = clean_string(divs[2].text)
  return (post_id, post_date, post_content) if post_content else None


def get_thread_post(bs4_tag, is_csv=False):
  if not is_csv:
    content = bs4_tag.find('div', {'class': POST_CLASS_CONTENT})
    return clean_string(content.text) or None
  return get_post_data(bs4_tag)


def get_thread_posts(url, pages, is_csv=False):
  post_list = []
  last_page = 1
  for page in pages:
    soup = get_response(get_paginated_url(url, page))
    if not soup:
      break
    last_page = page
    # remove embedded quotes, code blocks, and images
    for element in soup.find_all(class_=[POST_CLASS_QUOTE, POST_CLASS_CODE, POST_CLASS_IMAGE]):
      element.decompose()
    posts = list()
    for bs4_tag in soup.select(POST_PATH):
      post = get_thread_post(bs4_tag, is_csv)
      if post:
        posts.append(post)
    if len(posts) :
      post_list += posts
  return post_list, last_page


def get_link(bs4_tag, is_csv=False):
  url = '%s%s' % (ROOT_URL, bs4_tag['href'])
  return url if not is_csv else (str(get_resource_id(url)), url)


def get_link_list(url, pages, is_csv=False):
  link_list = []
  last_page = 1
  for page in pages:
    soup = get_response(get_paginated_url(url, page))
    if not soup:
      break
    last_page = page
    links = list(map(lambda x: get_link(x, is_csv), soup.select(ANCHOR_PATH)))
    link_list += links
  return link_list, last_page


def get_resource_data(url, pages, is_csv=False, is_thread=False):
  resource_id = get_resource_id(url)
  fn = get_thread_posts if is_thread else get_link_list
  data, last_page = fn(url, pages, is_csv)
  return data, last_page, resource_id
