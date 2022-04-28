#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/nurfnick/Data_Viz/blob/main/Content/Data_Collecting/11_Twitter.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# # Twitter a Social Media Scrape
# 

# ## Authorizing a Twitter Account

# First you'll need the [twitter package](https://pypi.org/project/twitter/)!  It is not automatically loaded into colab.  

# In[1]:


get_ipython().system('pip install twitter')


# Next you'll need the authentication codes for a twitter api.  You can use your own twitter account and follow the directions [here](https://developer.twitter.com/en/docs/authentication/oauth-1-0a/api-key-and-secret).  
# 
# For class I have shared some authentication keys.  In order to keep these secret (GitHub won't let us post secrets to their website!) I have created a file called `config.py`.  I upload this into the environment (file structure) of colab and I reference it like a package.  This means only if you have this file can you get to it but I can share my code with everyone still.

# In[3]:


import twitter
import config

CONSUMER_KEY = config.CONSUMER_KEY
CONSUMER_SECRET = config.CONSUMER_SECRET
OAUTH_TOKEN = config.OAUTH_TOKEN
OAUTH_TOKEN_SECRET = config.OAUTH_TOKEN_SECRET
auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

mathcs_twitter_api = twitter.Twitter(auth=auth)


# ## Posting to Social Media

# In[4]:


status = "Having fun in Data Processing and Vizualization class!  Posting to twitter has never been easier! On Monday"

mathcs_twitter_api.statuses.update(
    status=status)


# The above shows the tweet was made to my account.  You can even go find it!  Think about how great you life could be if you automate all your interactions with socials too!

# ## What is the Twitterverse Discussing?

# In[6]:


# The Yahoo! Where On Earth ID for the entire world is 1.
# See https://dev.twitter.com/docs/api/1.1/get/trends/place and
# http://developer.yahoo.com/geo/geoplanet/

WORLD_WOE_ID = 1
US_WOE_ID = 23424977

# Prefix ID with the underscore for query string parameterization.
# Without the underscore, the twitter package appends the ID value
# to the URL itself as a special case keyword argument.

world_trends = mathcs_twitter_api.trends.place(_id=WORLD_WOE_ID)
us_trends = mathcs_twitter_api.trends.place(_id=US_WOE_ID)

for i in range(10):
    print(world_trends[0]['trends'][i]['query'])


# In[7]:


for i in range(3):
    print(us_trends[0]['trends'][i]['query'])


# Here is a nicer display of the data using `json` package.  JSON is anotherway to store data and is utilized in many no-sql databases.

# In[8]:


import json

print(json.dumps(world_trends, indent=1))
print(json.dumps(us_trends, indent=1))


# ### Computing the intersection of two sets of trends

# In[9]:


world_trends_set = set([trend['name'] 
                        for trend in world_trends[0]['trends']])

us_trends_set = set([trend['name'] 
                     for trend in us_trends[0]['trends']]) 

common_trends = world_trends_set.intersection(us_trends_set)

print(common_trends)


# ## Search Results

# In[11]:


#  Set this variable to a trending topic, 
# or anything else for that matter. The example query below
# was a trending topic when this content was being developed
# and is used throughout the remainder of this chapter.
import json


#q = "#Ada"
q = '#JasonRoy'

count = 1000

# See https://dev.twitter.com/docs/api/1.1/get/search/tweets

search_results = mathcs_twitter_api.search.tweets(q=q, count=count)

statuses = search_results['statuses']


# Iterate through 5 more batches of results by following the cursor

for _ in range(5):
    print("Length of statuses", len(statuses))
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError: # No more results when next_results doesn't exist
        break
        
    # Create a dictionary from next_results, which has the following form:
    # ?max_id=313519052523986943&q=NCAA&include_entities=1
    kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])
    
    search_results = mathcs_twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']

# Show one sample search result by slicing the list...
print(json.dumps(statuses, indent=4))


# In[13]:


len(statuses)


# In[14]:


json.dumps(statuses[1])


# ### Extracting text, screen names, and hashtags from tweets

# In[15]:


import time


status_texts = [ status['text'] 
                 for status in statuses ]

screen_names = [ user_mention['screen_name'] 
                 for status in statuses
                     for user_mention in status['entities']['user_mentions'] ]

hashtags = [ hashtag['text'] 
             for status in statuses
                 for hashtag in status['entities']['hashtags'] ]

# Compute a collection of all words from all tweets
words = [ w 
          for t in status_texts 
              for w in t.split() ]

# Explore the first 5 items for each...

print(json.dumps(status_texts[0:5], indent=1))
print(json.dumps(screen_names[0:5], indent=1))
print(json.dumps(hashtags[0:5], indent=1))
print(json.dumps(words[0:5], indent=1))


# In[16]:


update = ""

for i in range (0,len(status_texts)):
    update = update + status_texts[i]


# In[17]:


update


# ### Creating a basic frequency distribution from the words in tweets

# In[18]:


from collections import Counter



for item in [words, screen_names, hashtags]:
    c = Counter(item)
    print(c.most_common()[:10]) # top 10


# In[19]:


words


# In[20]:


from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pa


stupid= ["hi",'bye']
columns=["word"]
pa.DataFrame(stupid,  columns = columns)


stopwords = set(STOPWORDS)




wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(update)

# plot the WordCloud image                       
plt.figure(figsize = (8, 8))
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)

#plt.show()
plt.savefig('img.png')


# In[ ]:


from PIL import Image

im = Image.open('img.png')


# In[ ]:


im


# ### Using Prettytable

# In[21]:


from prettytable import PrettyTable

for label, data in (('Word', words), 
                    ('Screen Name', screen_names), 
                    ('Hashtag', hashtags)):
    pt = PrettyTable(field_names=[label, 'Count']) 
    c = Counter(data)
    [ pt.add_row(kv) for kv in c.most_common()[:10] ]
    pt.align[label], pt.align['Count'] = 'l', 'r' # Set column alignment
    print(pt)


# ### Calculating Lexical Diversity

# In[ ]:


# A function for computing lexical diversity
def lexical_diversity(tokens):
    return 1.0*len(set(tokens))/len(tokens) 

# A function for computing the average number of words per tweet
def average_words(statuses):
    total_words = sum([ len(s.split()) for s in statuses ]) 
    return 1.0*total_words/len(statuses)

print(lexical_diversity(words))
print(lexical_diversity(screen_names))
print(lexical_diversity(hashtags))
print(average_words(status_texts))


# ### Finding the most popular retweets

# In[22]:


retweets = [
            # Store out a tuple of these three values ...
            (status['retweet_count'], 
             status['retweeted_status']['user']['screen_name'],
             status['text']) 
            
            # ... for each status ...
            for status in statuses 
            
            # ... so long as the status meets this condition.
                if 'retweeted_status' in status
           ]

# Slice off the first 5 from the sorted results and display each item in the tuple

pt = PrettyTable(field_names=['Count', 'Screen Name', 'Text'])
[ pt.add_row(row) for row in sorted(retweets, reverse=True)[:5] ]
pt.max_width['Text'] = 50
pt.align= 'l'
print(pt)


# ### Plotting frequencies of words

# In[ ]:


import matplotlib
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


word_counts = sorted(Counter(words).values(), reverse=True)



plt.loglog(word_counts)
plt.ylabel("Freq")
plt.xlabel("Word Rank")


# ### Posting It Back on the Web

# In[ ]:


import datetime
now = datetime.datetime.now()

print(now)


# In[ ]:


popular = c.most_common()[0][0]

now = datetime.date(now.year,now.month,now.day)

print(now)


# In[ ]:


mathcs_twitter_api.statuses.update(
    status="#ECUTigers are talking about {} today on {} @cs_ecu".format(popular,now))


# In[ ]:


mathcs_twitter_api.statuses.update(
    status="#ECUTigers are talking about {} today on {} @cs_ecu".format(popular,now))


# In[ ]:





# In[ ]:


retweets = [
            # Store out a tuple of these three values ...
            (status['retweeted_status']['user']['screen_name'],
             status['text']) 
            
            # ... for each status ...
            for status in statuses 
            
            # ... so long as the status meets this condition.
                if 'retweeted_status' in status
           ]


# In[ ]:


retweets[1]


# In[ ]:


mathcs_twitter_api.statuses.update(
    status="#ECUTigers are saying `{}` today on {} @cs_ecu".format(retweets[1],now))


# ## Getting Home Pages and Past Tweets

# We can grab the home timeline from our user.

# In[23]:


len(mathcs_twitter_api.statuses.home_timeline())


# Or another user

# In[ ]:


len(mathcs_twitter_api.statuses.user_timeline(screen_name="nurfnick"))


# I am going to guess here that the API is limiting me to only the past 20 tweets.  You'll find that there are lots of limits in the API!

# ## Your Turn

# Using either the math_cs credentials or your own;
# 
# 1. Get authenticated to twitter.
# 2. Find the top trending 10 topics in the world and display them by name
# 3. Search for your favorite show, actor, sports team or player and see what twitter is saying about them.

# In[ ]:




