from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import os
import pandas as pd

java_path = "C:\\Program Files (x86)\\Java\\jre1.8.0_121\\bin\\java.exe"
os.environ['JAVAHOME'] = java_path
st = StanfordNERTagger('E:\\Hobby projects\\TripAdvicer\\TripAdvicer\\jars\\english.all.3class.distsim.crf.ser.gz',
                       'E:\\Hobby projects\\TripAdvicer\\TripAdvicer\\jars\\stanford-ner.jar', encoding='utf-8')
review_df = pd.read_csv('E:\\Hobby projects\\TripAdvicer\\hotel_rating1.csv', header=None, encoding='ISO-8859-1',
                            names=['name', 'date', 'location', 'rating', 'subject', 'review'])
text = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'
text1 = st.tag(word_tokenize(text))
print(str(text1))

def name_entity_token(val):
	classified_text = ''
	sentences = sent_tokenize(val)
	for sentence in sentences:
		text = st.tag(word_tokenize(sentence))
		#print(text)
		classified_text = classified_text + str(text)
	#print(classified_text)
	return(classified_text)
review_df['ner_tag'] = review_df['review'].apply(lambda x: name_entity_token(x))