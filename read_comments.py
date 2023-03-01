import argparse
import re
import json
from networkx import ladder_graph
import pandas as pd
import spacy

# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_sm")
black_list = ["i", "I", "you", "You", "YOU", "she", "She", "SHE", "he", "He", "HE", "it", "It", "IT", "our", "Our", "OUR", "they", "They", "THEY", "me", "Me", "ME", "him", "Him", "HIM", "her", "Her", "HER", "us", "Us", "US", "them", "Them", "THEM", "my", "My", "MY", "your", "Your", "YOUR", "his", "His", "HIS", "our", "Our", "OUR", "their", "Their", "THEIR", "mine", "Mine", "MINE", "myself", "Myself","MYSELF", "yourself", "Yourself", "YOURSELF", "himself", "Himself", "HIMSELF", "herslef", "Herself", "HERSELF", "itself", "Itself", "ITSELF," "ourselves", "Ourselves", "OURSELVES", "themselves", "Themselves", "THEMSELVES",  "yourselves", "Yourselves", "YOURSELVES", "this", "that"]
black_list = set(black_list)
def main():

    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--comments_file', default=None, type=str, required=True, help='Comments file')
    parser.add_argument('--subreddits_file', default=None, type=str, required=False, help='Subreddits file')
    parser.add_argument('--target_dir', default=None, type=str, required=False, help='Directory to store comments')
    args = parser.parse_args()

    # Read subreddits
    if args.subreddits_file:
        with open(args.subreddits_file, 'r') as f:
            subreddits = set(f.read().strip().split('\n'))

    # Load comments in chunks
    comments = list()
    for c in pd.read_json(args.comments_file, compression='bz2', lines=True, dtype=False, chunksize=10000):
        if args.subreddits_file:
            c = c[c.subreddit.isin(subreddits)]
        comments.append(c)
    comments = pd.concat(comments, sort=True)
    print(type(comments))
    # Do something with comments here

    # Store extracted comments
    l=[]
    if args.target_dir:
        target_file = '{}/comments_extracted_{}.txt'.format(
            args.target_dir, re.findall(r'\d{4}-\d{2}', args.comments_file)[0]
        )
 #       comments.to_json(
 #           target_file,
 #           orient='records',
 #           lines=True
 #       )
        dictionary = comments.to_dict('dict')
        #all usernames 
        for i in range (len(list(dictionary.values())[2])):
            #print(i)
            doc = nlp(list(dictionary.values())[2][i])
            for chunk in doc.noun_chunks:
              if len(chunk.text) > 3:
                concept_candidate = set(chunk.text.split())
                if not bool(concept_candidate & black_list):
                    temp_list = [chunk.text.encode('utf-8')]
                    l += temp_list

        #all cleaned body
        #print(list(dictionary.values())[2])
        #with open(target_file, "w") as outfile:
        #    json.dump(dictionary, outfile)
        with open(target_file, 'w') as fp:
            for item in l:
                # write each item on a new line
                fp.write("%s\n" % item)
if __name__ == '__main__':
    main()
