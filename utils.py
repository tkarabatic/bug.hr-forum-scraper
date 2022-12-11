from datetime import date, timedelta
from time import strptime
import os
import re
import requests
from constants import CONTENT_CLASS_SUBFORUM, CONTENT_CLASS_THREAD
from bs4 import BeautifulSoup


def get_path(filename):
    CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(CURRENT_FOLDER, filename)


def get_filename(page_start='', page_end='', base='', subforum_id='', thread_id='', pid_start='', pid_end=''):
  name = base or 'bug_forum_sub'
  if subforum_id:
    name = name + '_' + str(subforum_id)
  if thread_id:
    name = name + '_thr_' + str(thread_id)
  if pid_start or pid_end:
    name = name + '_pid' + str(pid_start)
    if pid_end:
      name = name + '-' + str(pid_end)
  elif page_start or page_end:
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
    print('Stored %d rows in "%s".' % (len(rows), file_path))


def clean_string(text):
  return re.sub(r'\s+', ' ', text).strip()


def sanitize_quotes(text):
  return '"%s"' % text.replace('"', '\\"')


def is_after(date, date_to_compare):
  return strptime(date, '%Y-%m-%d') > strptime(date_to_compare, '%Y-%m-%d')


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


def get_date_diff_days(first_date_str, second_date_str):
  first_date = date(*map(int, first_date_str.split('-')))
  second_date = date(*map(int, second_date_str.split('-')))
  return abs(second_date - first_date).days


def get_date_string(timestamp):
  is_yesterday = timestamp.startswith('jučer')
  if is_yesterday or timestamp.startswith('danas'):
    today = date.today()
    return '%s' % (today - timedelta(days=1) if is_yesterday else today)
  date_regex = re.compile(r'(?P<day>\d{,2}).(?P<month>\d{,2}).(?P<year>\d{4})')
  res = date_regex.search(timestamp).groupdict()
  return '%s-%s-%s' % (res['year'], res['month'].zfill(2), res['day'].zfill(2))


def get_resource_id(string, is_filename=False):
  regex = r'.*_(?P<id>\d+)_p.*.txt' if is_filename else r'.*/(?P<id>\d+).aspx'
  id_regex = re.compile(regex)
  return id_regex.search(string).group('id')


def get_int(string):
  try:
    return int(string or '')
  except:
    return 0


def get_post_ids(string):
  regex = re.compile(r'.*_pid(?P<id_min>\d+)-{0,1}(?P<id_max>\d*)\.\s*')
  res = regex.search(string)
  if not res:
    return '', ''
  return get_int(res.group('id_min')), get_int(res.group('id_max'))


def store_data_rows(data, is_txt, is_csv, page_start, page_end, name='', subforum_id='', thread_id='', folder_name='', pid_start='', pid_end=''):
  filename = get_filename(page_start, page_end, name, subforum_id, thread_id, pid_start, pid_end)
  if is_txt:
    rows = data if not is_csv else list(map(lambda x: x[-1], data))
    store_to_file(rows, '%s.txt' % filename, folder_name)
  if is_csv:
    rows = list(map(lambda x: ','.join(x[:-1] + (sanitize_quotes(x[-1]),)), data))
    store_to_file(rows, '%s.csv' % filename, folder_name)


def get_pages(args):
  page_start = args.page or 1
  page_end = (args.page_end if (args.page_end and args.page_end >= page_start) else page_start) + 1
  return page_start, page_end
