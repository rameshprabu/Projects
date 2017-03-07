import pandas as pd
from nltk.corpus import stopwords
import unicodedata
import nltk
from nltk import word_tokenize
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import textmining
from nltk import pos_tag
import regex as re
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer



def load_data(filepath,colnames):
    #load the reviews from the csv file
    review_df = pd.read_csv(filepath,header=None,encoding='ISO-8859-1',names=colnames)
    #read the positive word corpus from the file and convert into an array
    pos_sent = open("positive.txt").read()
    positive_words = pos_sent.split('\n')
    # read the negative word corpus from the file and convert into an array
    neg_sent = open("negative.txt").read()
    negative_words = neg_sent.split('\n')
    return review_df,positive_words,negative_words

#Get the country from the location col(city|country)
def get_country(val):
    txt = val.split('|')
    if(len(txt)==1):
        country = txt[0]
    else:
        country = txt[1]
    return country.lower().strip()


def data_preprocessing(review_df):
    #remove the stop words from the data
    stop = stopwords.words('english')
    review_df['subject_pross'] = review_df['subject'].apply(lambda x: ' '.join([words for words in str(x).split(" ") if words not in stop]))
    review_df['review_pross'] = review_df['review'].apply(lambda x: ' '.join([words for words in str(x).split(" ") if words not in stop]))

    #Lemmatize words so that suffix and prefix is removed . Higher match between words can be optained with this process
    wnl = nltk.WordNetLemmatizer()
    review_df['subject_pross'] = review_df['subject_pross'].apply(lambda x: word_tokenize(x))
    review_df['subject_pross'] = review_df['subject_pross'].apply(lambda x: " ".join(wnl.lemmatize(t) for t in x))
    review_df['review_pross'] = review_df['review_pross'].apply(lambda x: word_tokenize(x))
    review_df['review_pross'] = review_df['review_pross'].apply(lambda x: " ".join(wnl.lemmatize(t) for t in x))
    return review_df

#Extract a sentence from a paragraph which matches the pattern
def extract_line(val,regex_pattern):
    match = re.findall(regex_pattern,val,flags=re.IGNORECASE)
    return match

# Tag the parts of speech of the input paragraph using NLTK package
def pos_tagging(review_df,input_col,output_col):
    review_df[output_col] = review_df[input_col].apply(lambda x: nltk.pos_tag(word_tokenize(str(x))) if x else "")
    return review_df

#Extract a given pattern from the POS tagged paragraph.
def chunkerParser(review_df,output_col,pos_col,regexPat):
    #pattern to identify unwanted pattern such as ' " \
    unwantedPat = r'[\"\',\[\]]'
    chunkParser = nltk.RegexpParser(regexPat)
    chunked = []
    i = 0
    for activities in review_df[pos_col]:
        treeleaf = ""
        chunked.append(chunkParser.parse(activities))
        for ch in chunked[i]:
            if str(ch).split(' ', 1)[0] == "(Chunk":
                wrapped = "(ROOT " + str(ch) + " )"  # Add a "root" node at the top
                trees = nltk.Tree.fromstring(wrapped, read_leaf=lambda x: x.split("/")[0])
                #extact the strings for the matched pattern
                for tree in trees:
                    treeleaf = str(treeleaf) + str(tree.leaves())
                #joining with ; to identify multiple matched patterns
                treeleaf = treeleaf + ';'
        # substitue the unwanted pattern with empty char
        review_df.loc[i,output_col] = re.sub(unwantedPat,'', treeleaf)
        i += 1
    return review_df


#Based on the subtopics it identifies the sentence which talk about. Extracts those sentence. POS tag that Sentence and Identify the sentiment of it
def analyse_subtopics(review_df,inputCol,lineCol,posCol,sentiCol,regPattern,positive_words,negative_words):
    review_df[lineCol] = review_df[inputCol].apply(lambda x: extract_line(x, regPattern))
    review_df[posCol] = review_df[lineCol].apply(lambda x: nltk.pos_tag(word_tokenize(str(x))) if x else "")
    review_df[sentiCol] = review_df[lineCol].apply(lambda x: sentiment_finder(x,positive_words,negative_words))
    return review_df

#Extract the key words using inverse term document frequency
def tfidf_string(val):
    tfidf = TfidfVectorizer(min_df=1)
    tfs = tfidf.fit_transform(word_tokenize(str(val)))
    feature_names = tfidf.get_feature_names()
    feature_string = ' '.join(feature_names)
    return feature_string

#Identifies the sentiment of the given input by comparing each word if it is present in the postive and negative word corpus. Returns a total sentiment
def sentiment_finder(val,positive_words,negative_words):
    positive_counter = 0
    negative_counter = 0
    total_sentiment = 0
    if val:
        val = ''.join(val)
        val = val.lower()
        for p in list(punctuation):
            val = val.replace(p, '')
        words = val.split(' ')
        word_count = len(words)
        for word in words:
            if word in positive_words:
                positive_counter = positive_counter + 1
            elif word in negative_words:
                negative_counter = negative_counter + 1
        total_sentiment = positive_counter-negative_counter
    return total_sentiment


#creates a word cloud for the input data

def create_cloud(text_to_draw, filename):
    wordcloud = WordCloud().generate(text_to_draw)
    plt.imshow(wordcloud)
    plt.axis("off")
    # take relative word frequencies into account, lower max_font_size
    wordcloud = WordCloud(max_font_size=40, relative_scaling=.5).generate(text_to_draw)
    #wordcloud.to_file(path.join(d, filename))
    plt.figure()
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()



#load the data
review_df,positive_words,negative_words = load_data('E:\\Hobby projects\\TripAdvicer\\TripAdvicer\\input\\hotel_rating2.csv',['name', 'date', 'location', 'rating', 'subject', 'review'])

#Preprocess the data
review_df = data_preprocessing(review_df)
review_df['country'] = review_df['location'].apply(lambda x: get_country(x))
review_df['month_year'] = review_df['date'].apply(lambda x: x[3:])
review_df['review'] = review_df['review'].apply(lambda x: '.'+x+'.')


#review_df = pos_tagging(review_df,'review','review_pos')
#review_df = pos_tagging(review_df,'subject','subject_pos')


############################################################
#4.a category food
############################################################
food_regex_pat = r"([^.]*?(?:food|breakfast|lunch|dinner)[^.]*\.)"
review_df = analyse_subtopics(review_df,"review","food","food_pos","food_senti",food_regex_pat,positive_words,negative_words)

food_rule = r"""Chunk: {<JJ><NN.?>+}"""
review_df = chunkerParser(review_df,"foodkeyword","food_pos",food_rule)

############################################################
#4.b category Restaurant
############################################################
restaurant_regex_pat = r"([^.]*?restaurant[^.]*\.)"
review_df = analyse_subtopics(review_df,"review","resta","resta_pos","resta_senti",restaurant_regex_pat,positive_words,negative_words)

resta_rule = r"""Chunk: {<JJ><NN.?>+}"""
review_df = chunkerParser(review_df,"restakeyword","resta_pos",resta_rule)

############################################################
#4.d category Service
############################################################
service_regex_pat = r"([^.]*?service[^.]*\.)"
review_df = analyse_subtopics(review_df,"review","service","service_pos",'service_senti',service_regex_pat,positive_words,negative_words)

service_rule = r"""Chunk: {<JJ><NN.?>+}"""
review_df = chunkerParser(review_df,"servicekeyword","service_pos",food_rule)

############################################################
#4.c category Room
############################################################
room_regex_pat = r"([^.]*?room[^.]*\.)"
review_df = analyse_subtopics(review_df,"review","room","room_pos","room_senti",room_regex_pat,positive_words,negative_words)

room_rule = r"""Chunk: {<JJ><NN.?>+}"""
review_df = chunkerParser(review_df,"roomkeyword","room_pos",room_rule)

############################################################
#4.e category Price
############################################################
price_regex_pat = r"([^.]*?(?:price|cost)[^.]*\.)"
review_df = analyse_subtopics(review_df,"review","price","price_pos","price_senti",price_regex_pat,positive_words,negative_words)

price_rule = r"""Chunk: {<JJ><NN.?>+}"""
review_df = chunkerParser(review_df,"pricekeyword","price_pos",price_rule)

############################################################
#4.f category General
############################################################
review_df['subject_senti'] = review_df['subject_pross'].apply(lambda x: sentiment_finder(x,positive_words,negative_words))

############################################################
#4.b Sentiments
############################################################
review_df['review_senti'] = review_df['review_pross'].apply(lambda x: sentiment_finder(x,positive_words,negative_words))

############################################################
#4.c Keywords
############################################################
review_df['review_tfidf'] = review_df['review_pross'].apply(lambda x: tfidf_string(x))


#export_df=review_df.loc[:,['name','rating','country','month_year','food_senti','service_senti','resta_senti','price_senti','room_senti','review_senti','subject_senti']]
#export_df.to_csv("E:\\Hobby projects\\TripAdvicer\\hotel_rating.csv",index=False)
review_df.to_csv("E:\\Hobby projects\\TripAdvicer\\TripAdvicer\\output\\hotel_rating_output.csv",index=False)

