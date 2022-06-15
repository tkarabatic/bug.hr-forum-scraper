import argparse
from helpers import get_response, get_resource_data, ROOT_URL
from utils import get_filename, get_resource_id, store_data_rows

parser = argparse.ArgumentParser()
parser.add_argument('-fn', '--filename', help='specify the filename to use when storing output data (omit the extension)')
parser.add_argument('-pg', '--page', type=int, help='specify the start page')
parser.add_argument('-pge', '--page-end', type=int, help='specify the end page (inclusive)')
parser.add_argument('--subforum-list', help='generate a list of subforums', action='store_true')
parser.add_argument('-tl', '--thread-list', help='specify the subforum URL to generate a list of threads for')
parser.add_argument('-pl', '--post-list', help='specify the thread URL to generate a list of posts for')
parser.add_argument('-plm', '--post-list-multiple', help='specify the .txt file with thread URLs to generate post lists for')
parser.add_argument('--csv', help='store output data in a .csv file (default is .txt)', action='store_true')
parser.add_argument('--txt-csv', help='store output data in both .txt and .csv formats', action='store_true')

args, unknown = parser.parse_known_args()
is_csv = args.txt_csv or args.csv or False
is_txt = args.txt_csv or not args.csv

if args.post_list_multiple:
  with open(args.post_list_multiple) as file:
    subforum_id = get_resource_id(args.post_list_multiple, is_filename=True)
    while True:
      thread_url = file.readline().strip()
      # TODO: enable specifying starting thread id
      if not thread_url:
        break
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
