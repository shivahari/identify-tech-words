"""
This script will take a bunch words and identify technical jargon used
"""
import nltk 
import sys 
import os,re,requests
import input_conf
from textblob import TextBlob
from bs4 import BeautifulSoup
import nltk.corpus
import base64
import keyword
import nltk.tag, nltk.data

def get_lines(input_file):
    "Return the lines in the input file"
    fp = open(input_file,mode='r',encoding='utf-8')
    lines = fp.readlines()
    fp.close()
    lines = " ".join(lines)

    return lines 

def get_common_words():
    "Get the commonly used nouns"
    words_from_url = read_url_contents()
    words_from_input_file = get_lines('sample_nltk.txt')
    words_from_input_file = words_from_input_file.split(',')

def get_tech_jargon(input_lines):
    "Return a list of tech jargon found in the sentence"
    # function to test if something is a noun
    is_noun = lambda pos: 'NN' in pos[:2] 
    # Break the entence down to words
    tokenized = nltk.word_tokenize(input_lines)  
    #remove the Python keywords
    python_keywords = keyword.kwlist
    nouns = [word.lower() for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos) and word not in input_conf.stopwords and word not in set(nltk.corpus.stopwords.words('english'))] #and word.isalnum() and word not in python_keywords]
    nouns = [noun for noun in nouns if noun.isalnum() and noun not in python_keywords]
   
    return nouns

def read_training_urls(url_file):
    "Read the urls from training url file"
    try:
        fp = open(url_file,mode='r',encoding='utf-8')
        lines = fp.readlines()
        fp.close()
        urls = []
        for line in lines:
            if re.search(r'http(s)',line):
                urls.append(line.strip('\n'))
    except Exception as e:
        print(str(e))
        urls = None
    finally:
        return urls

def read_url_contents():
    "Open the urls from the url file and read the contents and return the most frequently used words"
    urls = read_training_urls('training-url.txt')
    relatednouns = []
    for url in urls:
        response = requests.get(url)
        html = response.text 
        soup = BeautifulSoup(html)
        nouns = get_tech_jargon(soup.text)
        relatednouns = relatednouns + nouns
    freq_words = nltk.FreqDist(relatednouns)

    return freq_words.most_common()

def create_pos_tag():
    "Create a new TECH pos tag"
    model = {}
    words_list = read_url_contents()
    for words in words_list:
        model.update({words[0]:'TECH'})
    tagger = nltk.tag.UnigramTagger(model=model)

    return tagger

#----START OF SCRIPT----
if __name__=='__main__':
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        if os.path.exists(os.path.abspath(input_filename)):
            lines = get_lines(input_filename)
            tagger = create_pos_tag()
            tokenized = nltk.word_tokenize(lines)
            tagged = tagger.tag(tokenized)
            tagged = [tag[0] for tag in tagged if tag[1]]
            print(set(tagged))
        else:
            print("Could not find the file %s"%sys.argv[1])
    else:
        print("USAGE: %s input_file"%__file__)
    