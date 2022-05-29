import os
import re
import requests


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


def get_response(url):
  response = requests.get(url)
  print('GET "%s", response status code %d' % (url, response.status_code))
  return response


def get_date_string(timestamp):
  date_regex = re.compile(r'(?P<day>\d{,2}).(?P<month>\d{,2}).(?P<year>\d{4})')
  res = date_regex.search(timestamp).groupdict()
  return '%s-%s-%s' % (res['year'], res['month'].zfill(2), res['day'].zfill(2))


def get_resource_id(url):
  id_regex = re.compile(r'.*/(?P<id>\d+).aspx')
  return id_regex.search(url).group('id')


def clean_string(text, escape_double_quotes=False):
  cleaned = re.sub(r'\s+', ' ', text).strip()
  return cleaned.replace('"', '\\"') if escape_double_quotes else cleaned
