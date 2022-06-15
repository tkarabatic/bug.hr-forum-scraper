import os
import re
import requests
from constants import CONTENT_CLASS_SUBFORUM, CONTENT_CLASS_THREAD
from bs4 import BeautifulSoup


def get_path(filename):
    CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(CURRENT_FOLDER, filename)


def get_filename(page_start, page_end, base='', subforum_id='', thread_id=''):
  name = base or 'bug_forum_sub'
  if subforum_id:
    name = name + '_' + str(subforum_id)
  if thread_id:
    name = name + '_thr_' + str(thread_id)
  name = name + '_p' + str(page_start)
  if page_start != page_end:
    name = name + '-' + str(page_end)
  return name


def store_to_file(rows, filename, folder_name='', mode='w+'):
  folder_path = get_path(folder_name) if folder_name else ''
  if folder_path and not os.path.exists(folder_path):
    os.makedirs(folder_path)
  file_path = os.path.join(folder_path, filename) if folder_path else get_path(filename)
  with open(file_path, mode) as file:
    for row in rows:
      file.write('%s\n' % row)
    print('Stored %d rows in "%s".' % (len(rows), filename))


def clean_string(text):
  return re.sub(r'\s+', ' ', text).strip()


def sanitize_quotes(text):
  return '"%s"' % text.replace('"', '\\"')


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
  # TODO: handle 'jucer/danas' case
  date_regex = re.compile(r'(?P<day>\d{,2}).(?P<month>\d{,2}).(?P<year>\d{4})')
  res = date_regex.search(timestamp).groupdict()
  return '%s-%s-%s' % (res['year'], res['month'].zfill(2), res['day'].zfill(2))


def get_resource_id(string, is_filename=False):
  regex = r'.*_(?P<id>\d+)_p.*.txt' if is_filename else r'.*/(?P<id>\d+).aspx'
  id_regex = re.compile(regex)
  return id_regex.search(string).group('id')


def store_data_rows(data, is_txt, is_csv, page_start, page_end, name='', subforum_id='', thread_id='', folder_name=''):
  filename = get_filename(page_start, page_end, name, subforum_id, thread_id)
  if is_txt:
    rows = data if not is_csv else list(map(lambda x: x[-1], data))
    store_to_file(rows, '%s.txt' % filename, folder_name)
  if is_csv:
    rows = list(map(lambda x: ','.join(x[:-1] + (sanitize_quotes(x[-1]),)), data))
    store_to_file(rows, '%s.csv' % filename, folder_name)
