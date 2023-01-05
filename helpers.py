from constants import (
  ANCHOR_PATH, POST_CLASS_CODE, POST_CLASS_CONTENT, POST_CLASS_DATE,
  POST_CLASS_IMAGE, POST_CLASS_MAIN, POST_CLASS_QUOTE, POST_PATH, ROOT_URL,
  SUBFORUM_TITLES
)
import csv
import os
import re
from math import floor
from utils import (
  clean_string, get_date_diff_days, get_date_string, get_path, get_resource_id,
  get_response, is_after
)


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
  if not len(divs):
    # there appears to be an edge case where a thread post with the 'post'
    # class contains a nested div that also has the 'post' class - which causes
    # get_thread_posts to include the child div in the result set, resulting
    # in an error in the mapping below, since the child 'post' only has text
    # content; such child divs can be safely ignored, since the parent already
    # provides the required content
    return None
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
      last_page = page
    else:
      break
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
    links = list(map(lambda x: get_link(x, is_csv), soup.select(ANCHOR_PATH)))
    if len(links):
      link_list += links
      last_page = page
    else:
      break
  return link_list, last_page


def get_resource_data(url, pages, is_csv=False, is_thread=False):
  resource_id = get_resource_id(url)
  fn = get_thread_posts if is_thread else get_link_list
  data, last_page = fn(url, pages, is_csv)
  return (data if len(data) else None), last_page, resource_id


def is_eligible_thread(stats):
  return stats['post_count'] > 20 and stats['file_count'] == 1 and stats['word_count'] < 100000 and stats['day_count'] > 14


def get_thread_stats(subforum_id):
  dir_path = get_path(subforum_id)
  dir_entries = os.scandir(dir_path) # note: the scanning is not sequential
  thread_stats = {}
  subforum_word_total = 0
  for entry in dir_entries:
    if not entry.name.endswith('.csv'):
      continue
    is_first_file = '_p1.' in entry.name or '_p1-' in entry.name
    thread_id = get_resource_id(entry.name.replace('.csv', '.txt'), True)
    thread_data = thread_stats.get(thread_id, {'id': thread_id, 'first_date': None, 'last_date': None, 'file_count': 0, 'post_count': 0, 'word_count': 0, 'day_count': 0 })
    with open(os.path.join(dir_path, entry.name), 'r') as file:
      csv_file = csv.reader(file)
      thread_data['file_count'] += 1
      for post in csv_file:
        if not post:
          break
        thread_data['post_count'] += 1
        post_date = post[1]
        if is_first_file and not thread_data['first_date']:
          thread_data['first_date'] = post_date
          if thread_data['last_date']:
            thread_data['day_count'] = get_date_diff_days(thread_data['last_date'], thread_data['first_date'])
        if not thread_data['last_date'] or is_after(post_date, thread_data['last_date']):
          thread_data['last_date'] = post_date
          if thread_data['first_date']:
            thread_data['day_count'] = get_date_diff_days(thread_data['last_date'], thread_data['first_date'])
        post_word_count = len(post[2].split())
        thread_data['word_count'] += post_word_count
        subforum_word_total += post_word_count
        thread_stats[thread_id] = thread_data

  threads = thread_stats.values()
  filtered_thread_stats = [x for x in threads if is_eligible_thread(x)]
  eligible_word_total = sum(map(lambda x: x['word_count'], filtered_thread_stats))
  print(f'subforum id: {subforum_id}')
  print(f'eligible threads: {len(filtered_thread_stats)} of {len(threads)}')
  print(f'eligible thread words: {eligible_word_total} of {subforum_word_total}')
  return filtered_thread_stats, eligible_word_total


def get_eligible_threads(subforum_ids, max_word_count=1000000):
  max_words_per_subforum = floor(max_word_count / len(subforum_ids))
  print(f'max words per subforum: { max_words_per_subforum}')
  threads_per_subforum = {}
  expended_words = 0
  for subforum_id in subforum_ids:
    threads, thread_word_total = get_thread_stats(subforum_id)
    thread_ids = [thread['id'] for thread in threads]
    subforum_word_count = thread_word_total
    max_words = max_words_per_subforum
    # if there are any unused words left, they are assigned to the last subforum
    if subforum_ids[-1] == subforum_id:
      max_words = max_word_count - expended_words
    if thread_word_total > max_words:
      selected_ids = []
      subforum_word_count = 0
      for thread in sorted(threads, key=lambda x: x['word_count'], reverse=True):
        if thread['word_count'] > (max_words - subforum_word_count):
          continue
        selected_ids.append(thread['id'])
        subforum_word_count += thread['word_count']
      thread_ids = selected_ids
    print(f'selected {len(thread_ids)} threads with {subforum_word_count} words for subforum {subforum_id}')
    print(f'total word count: {subforum_word_count + expended_words}\n')
    if len(thread_ids):  
      threads_per_subforum[subforum_id] = thread_ids
      expended_words += subforum_word_count
  return threads_per_subforum


def annotate_subforum(id):
  print(f'Annotating data for subforum {id}...')
  dir_path = get_path(id)
  dir_files = os.scandir(dir_path)
  with open(get_path(f'bug_subforum_{id}_annotated.txt'), 'a+') as annotated:
    name, parent_name = SUBFORUM_TITLES[id]
    annotated.write(f'<doc id="{id}" name="{name}" parent_forum_name="{parent_name}">')
    for dir_file in dir_files:
      if not dir_file.name.endswith('.csv'):
        continue
      print(f'Current file: {dir_file.name}')
      thread_id = dir_file.name.split('thr_')[1].split('_pid')[0]
      with open(os.path.join(dir_path, dir_file.name), 'r') as file:
        csv_file = csv.reader(file)
        for post in csv_file:
          if not post:
            break
          year, month, *_ = post[1].split('-')
          annotated.write(f'<post id="{post[0]}" date="{post[1]}" thread_id="{thread_id}" year="{year}" month="{month}">{post[2]}</post>')
    annotated.write('</doc>')

