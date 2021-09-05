import requests
from bs4 import BeautifulSoup as soup

#A set of functions that:
#1. Parses a url given via input
#2. Extracts the review list info of url
#huLui Sentiment
#nrc Sentiment
#vader Sentiment
#3. Extracts key info from review itself
#4. That takes each url in 2. and runs 3. function to create a dictionary of review info
#5. Add new review entries to csv file

#1.
def urlParse(link):
    import requests
    from bs4 import BeautifulSoup as soup
    reqUrl = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    if reqUrl.status_code == 200:
        return soup(reqUrl.text, 'html.parser')
    else:
        print('The link ' + str(link) + ' has failed to parse and has caused a status code 200 error') 


#2.
def theList(page):
    games = page.find_all('div', attrs={'class':'clear itemList-item'})
    print(str(len(games)) + ' review links have been added to the main review list')
    for game in games:
        title = game.find("div", attrs={"class":"item-title"}).find('a').get_text().strip()
        link = game.find("div", attrs={"class":"item-title"}).find('a').get('href')
        genre = game.find('span', attrs={'class':'item-genre'}).get_text().strip()
        platform = game.find('span', attrs={'class':'item-platform'}).get_text().strip()
        reviews.append((title,link,genre,platform))
    print('Main review list has been updated with key information appended')
    #try/except - print title - else print link - else print title failed
    #find out type of error if none == true / may enclose for loop into try/except and name game that has broken

#2.5
def getReview(url):
    import requests
    from bs4 import BeautifulSoup as soup
    reqTotal = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) 
    if reqTotal.status_code == 200:
        pageTotal = soup(reqTotal.text, 'html.parser')
        paras = pageTotal.find_all('p')
        nocode = list() #Create empty list to add text to
        for i in range(len(paras)):
            nocode.append(paras[i].get_text())
        fullreview = ' [New Paragraph] '.join(str(x) for x in nocode)
        fullreview = fullreview.replace('\n','')
        return fullreview 
    else:
        print('We were unable to extract main review text from ' + str(url))



#Sentiment 1
def get_posnegWords(url):
    import requests
    words = requests.get(url).content.decode('latin-1')
    word_list = words.split('\n')
    index = 0
    while index < len(word_list):
        word = word_list[index]
        if ';' in word or not word:
            word_list.pop(index)
        else:
            index+=1
    return word_list

def huLiu_sentiment(text):
    from nltk import word_tokenize
    posTrack = 0
    negTrack = 0
    sentiment_field = list()
    for word in word_tokenize(text):
        if word in positive_words:
            posTrack+=1
        if word in negative_words:
            negTrack+=1
    
    pos = posTrack/len(word_tokenize(text))*100 #calculate % of positive
    neg = negTrack/len(word_tokenize(text))*100 #calculate % of negative
    difference = (posTrack-negTrack)/len(word_tokenize(text))*100
    try:
        percentPos = pos//(pos+neg)*100 #calculate % of positive words out of positive/negative together
        #ZeroDivisionError: float division by zero
    except ZeroDivisionError:
        percentPos = 'N/A'
    sentiment_field.append((pos,neg,difference,percentPos))
    return sentiment_field


#nrc Sentiment
def get_nrc_words():
    nrc = "\\NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt"
    count=0 
    emotion_dict=dict() 
    with open(nrc,'r') as f: 
        all_lines = list() 
        for line in f: 
            if count < 46: 
                count+=1
                continue
            line = line.strip().split('\t')
            
            if int(line[2]) == 1: 
                if emotion_dict.get(line[0]): 
                    emotion_dict[line[0]].append(line[1]) 
                else:
                    emotion_dict[line[0]] = [line[1]]
        #print emotion_dict has been created 
        return emotion_dict

emotion_dict = get_nrc_words()

def emotion_analyzer(text,emotion_dict=emotion_dict): 
    emotions = {x for y in emotion_dict.values() for x in y} #return set based on the following for-loops
    emotion_count = dict()
    for emotion in emotions:
        emotion_count[emotion] = 0 #sets each emotion e.g. anger, fear at 0

    total_words = len(text.split()) #splits text into list then returns total number of words
    for word in text.split(): #for each word in list of words
        if emotion_dict.get(word): #if that word is listed  in emotion_dict
            for emotion in emotion_dict.get(word): #for each emotion in dictionary of emotions (all currently set to zero)
                emotion_count[emotion] += 1/len(text.split()) 

    #sort emotions into ascending order top to bottom
    #from collections import OrderedDict
    #sorted_emotions = OrderedDict(sorted(emotion_count.items(), key=lambda t: t[1], reverse=True))

    return emotion_count

#vaderSentiment
def vader_comparison(texts):
    from nltk import sent_tokenize
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    headers = ['pos','neg','neu','compound']
    #print("'pos\t','neg\t','neu\t','compound'")
    analyzer = SentimentIntensityAnalyzer()
    sentences = sent_tokenize(texts)
    pos=compound=neu=neg=0
    for sentence in sentences:
        vs = analyzer.polarity_scores(sentence)
        pos+=vs['pos']/(len(sentences))
        compound+=vs['compound']/(len(sentences))
        neu+=vs['neu']/(len(sentences))
        neg+=vs['neg']/(len(sentences))
    vader_scores = {'v_positive':pos,'v_negative':neg,'v_neutral':neu,'v_compound':compound}
     #sort emotions into ascending order top to bottom
    #from collections import OrderedDict
    #vader_scores = OrderedDict(sorted(vader_scores.items(), key=lambda t: t[1], reverse=True))
    #vader_scores = str(vader_scores)
    return vader_scores

#wordLength
def reviewWords(text):
    from nltk import word_tokenize
    count = len(word_tokenize(text))
    return count



#3.
def reviewInfo(review,plat,genre):
    import requests
    from bs4 import BeautifulSoup as soup
    response = requests.get(review, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print('The link ' + str(review) + ' has failed') #add (review) link
        #else - skip to next link

    info = list() #google how to try/except a lot of stuff at the same time
    page = soup(response.text, 'html.parser')
    name = page.find('span', attrs={'class':'title-hover-link'}).get_text()
    try:
        author = page.find('span', attrs={'class':'author-name'}).get_text() #e.g. 'TJ Hafer'
    except:
        page.find('span', attrs={'itemprop': 'name'}).get_text().strip()
    #stars.find('span', attrs={'itemprop': 'name'}).get_text()
    subhead = page.find('div', attrs={'class':'article-subhead'}).get_text().strip() #String manipulation needed to remove Share & \n\n somehow
    subhead = subhead.replace('Share.\n\n','')
    subhead = subhead.strip()
    try:
        summary = page.find('div', attrs={'class':'review-bottom'}).find('p').get_text().strip() #verdict
        score = page.find('span', attrs={'itemprop':'ratingValue'}).get_text().strip() # e.g. 9.1
        blurb = page.find('div', attrs={'class':'blurb'}).get_text().strip() #e.g. 'Four fun, distinct factions and a story-driven campaign in Total War: Warhammer 2 set a new bar for the series.'
        published = page.find('span', attrs={'class':'publish-date'}).get_text() #e.g. 25 Sep 17
    except:
        responseTwo = requests.get(str(review + '?page=2'), headers={'User-Agent': 'Mozilla/5.0'})
        pageTwo = soup(responseTwo.text, 'html.parser')
        summary = pageTwo.find('div', attrs={'class':'review-bottom'}).find('p').get_text().strip()
        score = pageTwo.find('span', attrs={'itemprop':'ratingValue'}).get_text().strip()
        blurb = pageTwo.find('div', attrs={'class':'blurb'}).get_text().strip()
        published = pageTwo.find('span', attrs={'class':'publish-date'}).get_text() #e.g. 25 Sep 17
        mainBody = getReview(review)
        mainTwo = getReview(str(review + '?page=2'))
        mainBody = str(mainBody + mainTwo)
        
    
    try:
	    platform = page.find('div', attrs={'class':'objectcard-object-platforms-first'}).get_text().strip() #e.g. PC
    except:
	    platform = plat

    #if pageTwo in locals():

    mainBody = getReview(review)
    huSentiment = huLiu_sentiment(mainBody)
    nrcSentiment = emotion_analyzer(mainBody)
    vaderSentiment = vader_comparison(mainBody)
    wordLength = reviewWords(mainBody)
    summarySentiment = huLiu_sentiment(summary)
    

    #incase of more errors with NoneType Attribute Errors

    #for i in d:
    #if i is None: #if i == None is also valid but slower and not recommended by PEP8
        #e.append("None")
    #else:
        #e.append(i)

    #Short Version:

    #['None' if v is None else v for v in d]
    try:
        info.append((name,author,subhead,summary,mainBody,score,blurb,published,wordLength,summarySentiment,huSentiment,nrcSentiment,vaderSentiment,platform,genre))
        pages[name] = info
    except UnboundLocalError as b:
        b = 'Failed'
        author = 'Flopped'
        info.append((name,author,subhead,summary,mainBody,score,blurb,published,wordLength,summarySentiment,huSentiment,nrcSentiment,vaderSentiment,platform,genre))
        pages[name] = info
        

#4.
def updateReviewInfo():
    for element in reviews:
        try:
            reviewInfo(element[1],element[3],element[2])
            #reviews.append((title,link,genre,platform))
            print('All key information from ' + element[0] + ' has been added to dictionary of reviews')
        except AttributeError:
            try:
                reviewInfo(str(element[1] + '?page=2'),element[3],element[2])
            except Exception as e:
                print('One of the values in ' + str(element[1]) + ' failed to be extracted')
                print(e)
        except (requests.exceptions.MissingSchema) as e:
            print(e)
            print('Missing schema occured. status')
            print(element[1])

    

#4.5
#Clean up Pages
#def cleanUpPages: #test on single dictionary entry
    #for page in pages: #go into each dictionary entry and....
        #for i in page:
            #i[8] = huSentiment (can't refer to directly as it's out of reviewInfo function and is now a list item)
            #i[9] = nrcSentiment
            #i[10] = vaderSentiment


#5.
def addReviewsToCSV():
    import csv
    with open("\\IGN Reviews 1.csv", 'a', newline='',encoding="utf-8") as file:
        a = csv.writer(file, delimiter=',')
        #Only run headers 1 time in write mode, then append mode for new entries
        #Add genre
        #headers = ['Name','Author', 'Subhead', 'Summary', 'Main Body', 'Score', 'Verdict','Publish Date', 'Review Word Count', 'Summary Sentiment', 'Hu Sentiment', 'NRC Sentiment', 'VaderSentiment', 'Platforms', 'Genre']
        #    info.append((name,author,subhead,summary,mainBody,score,blurb,published,wordLength,summarySentiment,huSentiment,nrcSentiment,vaderSentiment,platform,genre))
        #a.writerow(headers)
        for page in pages:
            a.writerow(pages[page][0])
            print(page + " has been uploaded")
    #close file



link = input()
page = urlParse(link)
reviews = list()
theList(page)
print('\n' + 'Testing element in review list' + '\n' + str(reviews[3]) + '\n')
pages = dict()
print('Testing link before extracting Review Info from each page \n' + str(reviews[3][1]) + '\n')

p_url = 'http://ptrckprry.com/course/ssd/data/positive-words.txt'
n_url = 'http://ptrckprry.com/course/ssd/data/negative-words.txt'
positive_words = get_posnegWords(p_url)
negative_words = get_posnegWords(n_url)
print('Within Hu and Liu\'s sentiment analysis lexicon:')
print('There are ' + str(len(positive_words)) + ' positive words and ' + str(len(negative_words)) + ' negative words' )

updateReviewInfo()
addReviewsToCSV()

    
