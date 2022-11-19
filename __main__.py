import argparse
import glob
from helpers import (
  get_eligible_threads, get_link_list, get_response, get_resource_data,
  get_thread_stats, ROOT_URL
)
import os
import re
from utils import get_path, get_resource_id, store_data_rows
from zipfile import ZipFile

parser = argparse.ArgumentParser()
# TODO: remove the '-fn' option (not used)
parser.add_argument('-fn', '--filename', help='specify the filename to use when storing output data (omit the extension)')
parser.add_argument('-pg', '--page', type=int, help='specify the start page')
parser.add_argument('-pge', '--page-end', type=int, help='specify the end page (inclusive)')
parser.add_argument('--subforum-list', help='generate a list of subforums', action='store_true')
parser.add_argument('-tl', '--thread-list', help='specify the subforum URL to generate a list of threads for')
parser.add_argument('-pl', '--post-list', help='specify the thread URL to generate a list of posts for')
parser.add_argument('-plm', '--post-list-multiple', help='specify the .txt file with thread URLs to generate post lists for')
parser.add_argument('-tid', '--thread-id', type=int, help='specify the thread id to start downloading from (used in conjunction with -plm)')
parser.add_argument('--csv', help='store output data in a .csv file (default is .txt)', action='store_true')
parser.add_argument('--txt-csv', help='store output data in both .txt and .csv formats', action='store_true')
parser.add_argument('-ts', '--thread-stats', nargs='+', help='specify the subforum id(s) to generate thread stats for')
parser.add_argument('-zs', '--zip-subforums', help='specify the file (generated using --thread-stats) to zip subforum thread files from')

args, unknown = parser.parse_known_args()
is_csv = args.txt_csv or args.csv or False
is_txt = args.txt_csv or not args.csv

if args.thread_stats:
  thread_ids_per_subforum = get_eligible_threads(args.thread_stats)
  data = []
  for subforum_id, thread_ids in thread_ids_per_subforum.items():
    print(subforum_id, thread_ids)
    data.append(f"{subforum_id},{'|'.join(thread_ids)}")
  store_data_rows(data, is_txt=True, is_csv=False, page_start=1, page_end=1, name='_bug_subforum_selected_threads')
elif args.zip_subforums:
  print(args.zip_subforums)
  with open(get_path(args.zip_subforums), 'r') as file:
    for row in file.readlines():
      [subforum_id, threads] = row.strip().split(',')
      print(subforum_id, threads)
      thread_ids = threads.split('|')
      with ZipFile(f'_bug_subforum_{subforum_id}_selected_threads.zip', 'w') as zip:
        folder_path = os.path.join(get_path(subforum_id), '[!_]*.txt')
        for file in glob.iglob(folder_path):
          if re.search(f'.*_sub_{subforum_id}_thr_{threads}_.*', file):
            zip.write(file)
elif args.post_list_multiple:
  with open(args.post_list_multiple) as file:
    subforum_id = get_resource_id(args.post_list_multiple, is_filename=True)
    initial_thread_id = args.thread_id
    while True:
      thread_url = file.readline().strip()
      if not thread_url:
        break
      current_thread_id = get_resource_id(thread_url)
      print('thread id:', current_thread_id)
      if initial_thread_id:
        # the matching thread has still not been reached
        if current_thread_id != str(initial_thread_id):
          continue
        # the matching thread has been found; reset the flag
        initial_thread_id = None
      page_start = 1
      page_end = 101
      while True:
        pages = range(page_start, page_end)
        data, last_page, resource_id = get_resource_data(thread_url, pages, is_csv, is_thread=True)
        if not data:
          break
        store_data_rows(data, is_txt, is_csv, page_start, last_page, args.filename, subforum_id, thread_id=resource_id, folder_name=str(subforum_id))
        if last_page < (page_end - 1):  # no additional pages are available
          break
        page_start += 100
        page_end += 100
else:
  page_start = args.page or 1
  page_end = (args.page_end if (args.page_end and args.page_end >= page_start) else page_start) + 1
  pages = range(page_start, page_end)
  data = None
  subforum_id = ''
  thread_id = ''
  page_end = pages[:-1]

  if args.subforum_list:
    data, last_page = get_link_list(ROOT_URL, pages, is_csv)
    page_end = last_page
  elif args.thread_list:
    data, last_page, resource_id = get_resource_data(args.thread_list, pages, is_csv)
    subforum_id = resource_id
    page_end = last_page
  elif args.post_list:
    data, last_page, resource_id = get_resource_data(args.post_list, pages, is_csv, is_thread=True)
    thread_id = resource_id
    page_end = last_page

  if data:
    store_data_rows(data, is_txt, is_csv, pages[0], page_end, args.filename, subforum_id, thread_id)
