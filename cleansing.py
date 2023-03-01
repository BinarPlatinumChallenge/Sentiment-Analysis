import pandas as pd
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words=(stopwords.words('indonesian'))

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
stop_factory = StopWordRemoverFactory()
sastrawi_stop_words = stop_factory.get_stop_words()
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()

stopword_dict = pd.read_csv('./dictionaries/stopwordbahasa.csv', header=None, names=['stopword'], encoding='latin-1')
stopword_dict = list(stopword_dict['stopword']) + sastrawi_stop_words + stop_words + ['ya','yg','ga','yuk','dah','sih','gue','nya','nih']
stopword_dict = list(dict.fromkeys(stopword_dict))
stopword_dict = filter(lambda word: word !='tidak', stopword_dict)
stopword_dict = list(stopword_dict)

import re
def lowercase(text):
  text = text.strip() 
  return text.lower()

def remove_unnecessary_char(text):
  text = re.sub('\\+n', ' ', text) # remove every new line
  text = re.sub('\n',' ',text) # remove every single new line
  text = re.sub('\\+', ' ', text) # remomove unessessary character
  text = re.sub(r'\brt\b','', text) # r'\b...\b to remove certain word, only at the beginning or end of the word for 'rt' 
  text = re.sub(r'\buser\b','', text) # r'\b...\b to remove certain word, only at the beginning or end of the word for 'user'
  text = re.sub(r'\burl\b','', text)
  text = re.sub(r'\bnurl\b','', text)
  text = re.sub('&lt;/?[a-z]+&gt;', '', text)
  text = re.sub('&amp', '', text)
  text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # remomove unessessary character 
  text = re.sub(':', ' ', text) # remomove special character 
  text = re.sub(';', ' ', text) 
  text = re.sub('  +', ' ', text) 
  text = re.sub(r'pic.twitter.com.[\w]+', '', text) # remomove unessessary character 
  text = re.sub(r'[^\x00-\x7F]+',' ', text)  
  text = re.sub(r'‚Ä¶', '', text)  
  to_delete = ['hypertext', 'transfer', 'protocol', 'over', 'secure', 'socket', 'layer', 'dtype', 'tweet', 'name', 'object'
                 ,'twitter','com', 'pic'] # delete another unessessary words
  for word in to_delete: 
      text = re.sub(word,'', text) # remove extra space
      text = re.sub(word.upper(),' ',text)
  return text

def remove_nonaplhanumeric(text):
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

def normalize_alay(text):
    alay_dict = pd.read_csv('./dictionaries/kamusalay.csv', names=['original', 'replacement'], encoding='latin-1')
    alay_dict_map = dict(zip(alay_dict['original'], alay_dict['replacement']))
    normalize_text = ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])
    return normalize_text

def remove_stopword(text):
    text = ' '.join(['' if word in stopword_dict else word for word in text.split(' ')])
    text = re.sub('  +', ' ', text)
    text = text.strip()
    return text

def remove_emoticon_byte(text):
   text = text.replace("\\", " ")
   text = re.sub(r'\bx..', ' ', text)
   text = re.sub(' n ', ' ', text)
   return text

def remove_early_space(text):
    if text[0] == ' ':
        return text[1:]
    else:
        return text

def handleTidak(text):
    words = text.split(' ')
    text = ' '.join(['tidak_' if words[i] == 'tidak' else words[i] for i in range(len(words))])
    text = text.strip()
    text = text.replace('tidak_ ','tidak_')
    return text

def stemming(text):
    return stemmer.stem(text)

def remove_number(text): #6
    text = ''.join([i for i in text if not i.isdigit()])
    text = re.sub('  +', ' ', text)
    text = text.strip()
    return text

def cleanse_text(text):
    text = lowercase(text) #1
    text = remove_unnecessary_char(text) #2
    text = remove_nonaplhanumeric(text) #3
    text = remove_emoticon_byte(text) #4
    text = remove_early_space(text) #5
    text = remove_number(text) #6
    text = normalize_alay(text) #8
    text = remove_stopword(text) #9
    text = stemming(text) #10
    text = handleTidak(text) #7
    return text