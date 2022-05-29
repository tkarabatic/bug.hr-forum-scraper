import argparse
from helpers import get_response, get_link_list, get_thread_posts, ROOT_URL
from utils import get_filename, get_resource_id, store_to_file

parser = argparse.ArgumentParser()
parser.add_argument('-fn', '--filename', help='specify the filename to use when storing output data (omit the extension)')
parser.add_argument('-pg', '--page', type=int, help='specify the start page')
parser.add_argument('-pge', '--page-end', type=int, help='specify the end page (inclusive)')
parser.add_argument('--subforum-list', help='generate a list of subforums', action='store_true')
parser.add_argument('-tl', '--thread-list', help='specify the subforum URL to generate a list of threads for')
parser.add_argument('-pl', '--post-list', help='specify the thread URL to generate a list of posts for')
parser.add_argument('--csv', help='store output data in a .csv file (default is .txt)', action='store_true')

args, unknown = parser.parse_known_args()
is_csv = args.csv or False
page_start = args.page or 1
page_end = args.page_end if (args.page_end and args.page_end >= page_start) else page_start
page_end += 1
pages = range(page_start, page_end)
if args.subforum_list:
  filename = get_filename(args.filename, is_csv=is_csv)
  store_to_file(filename, get_link_list(ROOT_URL, pages, is_csv))
elif args.thread_list:
  subforum_id = get_resource_id(args.thread_list)
  filename = get_filename(args.filename, pages, is_csv, subforum_id)
  store_to_file(filename, get_link_list(args.thread_list, pages, is_csv))
elif args.post_list:
  thread_id = get_resource_id(args.post_list)
  filename = get_filename(args.filename, pages, is_csv, thread_id=thread_id)
  store_to_file(filename, get_thread_posts(args.post_list, pages, is_csv))
