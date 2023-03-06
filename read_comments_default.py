import wget
from os.path import exists
import os
import zstandard 
import io
import json
from datetime import datetime
import argparse
import re
import spacy

parser = argparse.ArgumentParser()
parser.add_argument('--comments_file', default=None, type=str, required=True, help='Comments file')
parser.add_argument('--monthe', default=None, type=int, required=True, help='month')
parser.add_argument('--year', default=None, type=int, required=True, help='year')
args = parser.parse_args()

nlp = spacy.load("en_core_web_sm")
black_list = ["i", "I", "you", "You", "YOU", "she", "She", "SHE", "he", "He", "HE", "it", "It", "IT", "our", "Our", "OUR", "they", "They", "THEY", "me", "Me", "ME", "him", "Him", "HIM", "her", "Her", "HER", "us", "Us", "US", "them", "Them", "THEM", "my", "My", "MY", "your", "Your", "YOUR", "his", "His", "HIS", "our", "Our", "OUR", "their", "Their", "THEIR", "mine", "Mine", "MINE", "myself", "Myself","MYSELF", "yourself", "Yourself", "YOURSELF", "himself", "Himself", "HIMSELF", "herslef", "Herself", "HERSELF", "itself", "Itself", "ITSELF," "ourselves", "Ourselves", "OURSELVES", "themselves", "Themselves", "THEMSELVES",  "yourselves", "Yourselves", "YOURSELVES", "this", "that"]
default_subreddits =["announcements",
"Art","AskReddit","askscience","aww","blog","books","creepy","dataisbeautiful","DIY","Documentaries","EarthPorn","explainlikeimfive","Fitness",
"food","funny","Futurology","gadgets","gaming","GetMotivated","gifs","history","IAmA","InternetIsBeautiful","Jokes","LifeProTips","listentothis","mildlyinteresting",
"movies","Music","nosleep","nottheonion","oldschoolcool","personalfinance","philosophy","photoshopbattles","pics","science","Showerthoughts","space","sports","television","tifu","todayilearned","TwoXChromosomes","UpliftingNews","videos","writingprompts"]
black_list = set(black_list)

forbiden = ['[deleted]', None, '', '.', ':', '..', '/' , '/.', '/..']
month = args.month
year = args.year
comments_file =args.comments_file

#url = 'https://files.pushshift.io/reddit/submissions/RS_'+ args.year +'-'+ month +'.zst'
#filename = wget.download(url)
url = 'https://files.pushshift.io/reddit/comments/RC_'+ str(year) +'-'+ str(month) +'.zst'
filename = wget.download(url)
dict_concepts={}
target_dir ="/content"
for file in os.listdir("/content"):
  target_file = '{}/comments_extracted_default_{}.txt'.format(target_dir, re.findall(r'\d{4}-\d{2}', comments_file)[0])
  if file.endswith(".zst") :
        file_name = os.path.join("/content", file)
        with open(file_name, 'rb') as fh:
          dctx = zstandard.ZstdDecompressor(max_window_size=2147483648)
          stream_reader = dctx.stream_reader(fh)
          text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')
          for count, line in enumerate(text_stream):
              obj = json.loads(line)
              if obj['subreddit'] in default_subreddits:
                if obj['author'] != None and obj['author'] != '[deleted]' and obj['author'] != '' :
                  text = obj['body']
                  # remove newline characters
                  text = text.replace('\r\n', ' ')
                  # remove digits
                  text = re.sub(r'\d+', '', text)
                  # remove extra spaces
                  text = re.sub(r'\s+', ' ', text).strip()
                  # remove URLs from text
                  text = re.sub(r'http\S+', '', text)
                  # remove square brackets and their contents
                  text = re.sub(r'\[.*?\]', '', text)
                  # remove square paranteces and their contents
                  text = re.sub(r'\(.*?\)', '', text)
                  text = text.replace("\\", "")
                  doc = nlp(text)
                  for chunk in doc.noun_chunks:
                    if len(chunk.text) > 3:
                      concept_candidate = set(chunk.text.split())
                      if not bool(concept_candidate & black_list):
                          tmp = chunk.text
                          if tmp in dict_concepts:
                              dict_concepts[tmp] += 1
                          else:
                              dict_concepts[tmp] = 1

  with open(target_file, "w") as outfile:
      json.dump(dict_concepts, outfile)
