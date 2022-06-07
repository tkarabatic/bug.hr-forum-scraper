import os
import re
import requests
from constants import CONTENT_CLASS_SUBFORUM, CONTENT_CLASS_THREAD
from bs4 import BeautifulSoup


def get_path(filename):
    CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(CURRENT_FOLDER, filename)


def get_filename(base='', pages=None, is_csv=False, subforum_id='', thread_id=''):
  name = base or 'bug_forum_sub'
  if subforum_id:
    name = name + '_' + str(subforum_id)
  if thread_id:
    name = name + '_thr_' + str(thread_id)
  if pages:
    name = name + '_p' + str(pages[0])
    if pages[-1] != pages[0]:
      name = name + '-' + str(pages[-1])
  return name + ('.csv' if is_csv else '.txt')


def store_to_file(filename, rows, mode='w+'):
  with open(get_path(filename), mode) as file:
    for row in rows:
      file.write('%s\n' % row)


def clean_string(text, escape_double_quotes=False):
  cleaned = re.sub(r'\s+', ' ', text).strip()
  return cleaned.replace('"', '\\"') if escape_double_quotes else cleaned


def get_response(url):
  response = requests.get(url)
  print('GET "%s", response status code %d' % (url, response.status_code))
  if response.status_code != 200:
    # Note: querying for a non-existent subforum page triggers an error 500
    print('A problem has occurred.')
    return None
  # 'html.parser' is recommended over parsing 'res.text' to avoid character
  # encoding issues
  soup = BeautifulSoup(response.content, 'html.parser')
  # Note: the bug.hr site does not return a 404 response code for non-existent
  # thread pages, so we have to check for page content instead
  content = soup.find('div', {'class': [CONTENT_CLASS_SUBFORUM, CONTENT_CLASS_THREAD]})
  has_content = content and clean_string(content.text)
  return soup if has_content else None


def get_date_string(timestamp):
  date_regex = re.compile(r'(?P<day>\d{,2}).(?P<month>\d{,2}).(?P<year>\d{4})')
  res = date_regex.search(timestamp).groupdict()
  return '%s-%s-%s' % (res['year'], res['month'].zfill(2), res['day'].zfill(2))


def get_resource_id(url):
  id_regex = re.compile(r'.*/(?P<id>\d+).aspx')
  return id_regex.search(url).group('id')
