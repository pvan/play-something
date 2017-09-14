import re
import difflib
import random
import subprocess
import urllib.request
import urllib.parse

#
# selects a random line from a messy list of music (songs / artists / notes)
# and plays the first youtube video if it seems like a close enough match
# (requiring a closer match the less views it has)
#
# ideally we'll skip lines that are headers or notes
# but play anything that is an actual song / artist combo
#
#
# TODO:
#
# most false negatives are lines that are just artists..
# is there a way to check for that and ok them?
#
# batch run a test.. save list of passes and fails for manual double-checking
#
# could use a is_a_real_song?() function.. any interesting ideas?
#


INPUT_FILE = "D:\\~phil\\notes\\~lists\\music list WIP.txt"

def clean_string(line):

    line = line.lower()

    # only strip out of source, actually (not vid titles)
    # strip out any notes in () or []
    #line = re.sub("[\(\[].*?[\)\]]", "", line)

    line = line.replace(' w/o',' without')
    line = line.replace(' w/',' with')
    line = line.replace(' w.',' with')
    line = line.replace(' thru',' through')

    line = line.replace('’',"'")

    line = line.replace(',','')
    line = line.replace('"','')
    line = line.replace('?','')
    line = line.replace('-','')
    line = line.replace(':','')
    line = line.replace('.','')
    line = line.replace('!','')
    line = line.replace('“','')
    line = line.replace('”','')
    line = line.replace('_','')
    line = line.replace('|','')

    # keep and use to match or no?
    #line = line.replace('+','')
    #line = line.replace('&','')
    #line = line.replace('and','')
    #line = line.replace('the','')
    #line = line.replace('by','')


    line = line.strip()

    # if line.endswith(' and'):
    #     line = line[:-4]
    # if line.startswith('y '):
    #     line = line[2:]
    # if line.startswith('n '):
    #     line = line[2:]

    return line


def alpha_sort(text):
    words = text.split()
    words.sort()
    return " ".join(words)


def url_from_youtube_search(textToSearch):
    textToSearch = textToSearch.strip()
    query_string = urllib.parse.urlencode({"search_query" : textToSearch})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode("utf-8"))
    url = "http://www.youtube.com/watch?v=" + search_results[0]
    return url


def title_from_youtube_url(url):
    vid_html = urllib.request.urlopen(url)
    title = re.findall(r'<title[^>]*>([^<]+)</title>', vid_html.read().decode("utf-8"))[0]

    title = title.lower()

    # surely a better way...
    title = title.replace("&quot;", '"')
    title = title.replace("&amp;", '&')
    title = title.replace("&#39;", "'")

    #if title.endswith("- youtube"):
    title = title.replace("- youtube", "")

    return title


def views_from_youtube_url(url):
    vid_html = urllib.request.urlopen(url)
    # gotta be pretty fragile..
    views = re.findall(r'watch-view-count">(.*?) views<', vid_html.read().decode("utf-8"))[0]
    views = views.replace(',',"")

    return views






f = open(INPUT_FILE, 'r')
lines = f.readlines()


list = []
for line in lines:

    item = line

    # strip anything in [] or ()
    # or should we treat these as separate lines?
    item = re.sub("[\(\[].*?[\)\]]", "", item)

    # remove any timestamps
    item = re.sub(r'[0-9][0-9]?:[0-9][0-9]?:?[0-9]?[0-9]?', "", item)

    # remove any leading numbers like "4)"
    item = re.sub(r'^[0-9][0-9]?\)', "", item, flags=re.MULTILINE)
    # remove any leading numbers like "4."
    item = re.sub(r'^[0-9][0-9]?\.', "", item, flags=re.MULTILINE)

    item = clean_string(item)

    if item.isspace():
        continue
    if not re.search('[a-zA-Z]', item):  # needs at least 1 letter
        continue
    if len(item) > 100:
        continue

    list.append(item)


list.sort()

# for item in list:
#     print (item)


url = None
count = 1
vid_ok = False

# while count < 100:  # for testing
while not vid_ok:

    print("\ntry " + str(count))
    count = count + 1

    searchText = random.choice(list)


    print('searching youtube for... ' + searchText)
    url = url_from_youtube_search(searchText)
    desc = title_from_youtube_url(url)
    views = int(views_from_youtube_url(url))
    print("results found...")

    print(desc)
    print(str(views) + " hits")


    # sort words before comparing
    # can cause problems if same but one has
    # a bunch of trailing or leading stuff
    # but going with it for now
    orig = clean_string(searchText)
    orig = alpha_sort(orig)
    desc = clean_string(desc)
    desc = alpha_sort(desc)
    rating = float(difflib.SequenceMatcher(None, orig, desc).ratio())

    print("source text: " + orig)
    print("video title: " + desc)
    print("similar: " + str(rating))


    vid_ok = False

    # lower the rating, the more views it needs to be considered ok
    if rating >= 0.4 and rating < 0.5 and views > 1000000: vid_ok = True
    if rating >= 0.5 and rating < 0.6 and views > 100000: vid_ok = True
    if rating >= 0.6 and rating < 0.7 and views > 10000: vid_ok = True
    if rating >= 0.7 and rating < 0.8 and views > 1000: vid_ok = True
    if rating >= 0.8: vid_ok = True  # close matches are ok all the time

    if vid_ok: print ("vid ok to play!")
    else: print("skip vid, try again")

    print(url)





args = ["start", "chrome", "/new-window"]
args.append(url)
subprocess.call(args, shell=True)


