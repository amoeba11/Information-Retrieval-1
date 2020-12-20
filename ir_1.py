# -*- coding: utf-8 -*-
"""IR_1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QRUh5YbrLTgahL-HfFox1FDbtG0-yBSx

Dolly Khandelwal

# Import Libraries and Load Data
"""

!pip install nltk
!pip install matplotlib
!pip install numpy

import nltk
import numpy as np
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import PorterStemmer, SnowballStemmer
from nltk.stem.lancaster import LancasterStemmer
import matplotlib.pyplot as plt
from collections import Counter
CRTPOSTAGS = 'NN NNS NNP NNPS'.split()

LEM = WordNetLemmatizer()
PS = PorterStemmer()
SS = SnowballStemmer('english')
LS = LancasterStemmer()

class DataSet(object):
    def __init__(self):

      allDocs = {}
      with open('/documents.txt') as f:
        rawDocs = f.read().strip('/').split('/')
        for doc in rawDocs:
          doc = doc.strip().split('\n')
          allDocs[doc[0]] = ' '.join(doc[1:])

      self.docs = {}
      self.relevantDocIds = []
      with open('/relevance_assessment.txt') as f:
        q2D = f.read().strip().strip('/').split('/')
        for q in q2D:
          q = q.strip().split('\n')
          self.relevantDocIds.append(q[1].split())
          for doc in q[1].split():
            if doc not in self.docs:
              self.docs[doc] = allDocs[doc]
      
      self.queries = []
      with open('/query.txt') as f:
        rawQueries = f.read().strip().strip('/').split('/')
        for q in rawQueries:
          q = q.strip().split('\n')
          self.queries.append(q[1].strip())

    def executeQueries(self, i):
      p = []
      r = []
      ret = []
      for query, relevant in zip(self.queries, self.relevantDocIds):
        precision, recall, returned, relevantReturned, relevant = self.calcMetrics(relevant, i.queryGetMatchingDocs(query.lower().split()))
        p.append(precision)
        r.append(recall)
        ret.append(returned)
        print("Relevant : ", relevant, ", Returned : ", returned, ", RelevantReturned : ", relevantReturned)

      self.plotMetrics(p, r)
      print("Avg Precision : ", sum(p)/10, ", Recall : ", sum(r)/10, ", Avg Returned : ", sum(ret)/10)
      return p, r, ret

    def executeQueriesBi(self, bi):
      p = []
      r = []
      ret = []
      for query, relevant in zip(self.queries, self.relevantDocIds):
        precision, recall, returned, relevantReturned, relevant = self.calcMetrics(relevant, bi.queryGetMatchingDocs(query.lower()))
        p.append(precision)
        r.append(recall)
        ret.append(returned)
        print("Relevant : ", relevant, ", Returned : ", returned, ", RelevantReturned : ", relevantReturned)

      self.plotMetrics(p, r)
      print("Avg Precision : ", sum(p)/10, ", Recall : ", sum(r)/10, ", Avg Returned : ", sum(ret)/10)
      return p, r, ret


    def calcMetrics(self, relevant, returned):
      relevantReturned = 0
      for r in relevant:
        if r in returned:
          relevantReturned += 1
      return relevantReturned/len(returned) , relevantReturned/len(relevant), len(returned), relevantReturned, len(relevant)

    def plotMetrics(self, precision, recall):
      x = np.arange(1, 11)
      ax1 = plt.subplot(1,1,1)
      w = 0.3
      plt.xticks(x + w /2, x)
      prec = ax1.bar(x, precision, width=w, color='b', align='center')
      rec = ax1.bar(x + w, recall, width=w,color='g',align='center')
      plt.xlabel('Query Number')
      plt.legend([prec, rec],['Precision', 'Recall'])
      plt.show()
      
    def plotComp(self, bar1, bar2, typ, tag1, tag2) : 
      r1 = np.arange(1, 11)
      r2 = [x + 0.25 for x in r1]
      
      plt.bar(r1, bar1, width = 0.25, edgecolor='white', label = tag1)
      plt.bar(r2, bar2, width=0.25, edgecolor='white', label = tag2)
     
      plt.xlabel('Queries', fontweight='bold')
      
      if(typ == "P"):
        plt.ylabel('Precision', fontweight='bold')
      elif (typ == "R"):
        plt.ylabel('Recall', fontweight='bold')
      else:
        plt.ylabel('Value', fontweight='bold')
      
      plt.xticks(np.arange(1, 11))
     
      plt.legend()
      plt.show()

data = DataSet()



"""# Task - 1 """

class InvertedIndex(object):
 
  def __init__(self, docs, processes=[], freqThres=10000):
    self.invIndList = dict()      #maps terms to doc ids
    self.actualTermFreq = dict()  #dict mapping actual freq of each term
    self.freqThres = freqThres
    self.actualTerms = set()

    self.doPrepo = 0
    self.doStopWord = 0
    self.doPosTag = 0
    self.processtype = None

    for process in processes:
      if process == 'PREPO':
        self.doPrepo = 1
      elif process == 'SW':
        self.doStopWord = 1
      elif process == 'POS':
        self.doPosTag = 1
      elif process == 'LEM':
        self.processtype = 'LEM'
      elif process == 'STEM':
        self.processtype = 'STEM'
      elif process == 'LEM_TAG':
        self.processtype = 'LEM_TAG'
    
    #Construct Inverted Index List
    for docId, doc in docs.items():
      for term in doc.split():
        self.actualTerms.add(term)
        term = self.processTerm(term)
        if term not in self.invIndList:
          self.invIndList[term] = {docId}
          self.actualTermFreq[term] = 0
        elif docId not in self.invIndList[term]:
          self.invIndList[term].add(docId)
        self.actualTermFreq[term] += 1

  def processTerm(self, term, tag='nn'):
    if self.processtype is None:
      return term
    elif self.processtype == 'LEM':
      return LEM.lemmatize(term)
    elif self.processtype == 'LEM_TAG':
      return LEM.lemmatize(term,pos=tag[0])
    elif self.processtype == 'STEM':
      return PS.stem(term)
 
  def queryGetMatchingDocs(self, matchingTerms):
    # print("iii", matchingTerms)
    matchingDocs = set()

    TAGS = nltk.pos_tag(matchingTerms)
    # print(TAGS)

    foundPrep = int(not self.doPrepo)

    # print("i22")
    for term_, TAG in zip(matchingTerms, TAGS):
      term = self.processTerm(term_)
      # print(term, end=" ")
      
      cond = term in self.invIndList
      if self.doStopWord and cond:
        cond = (self.actualTermFreq[term] < self.freqThres)
      if self.doPosTag and cond:
        cond = (TAG[1] in CRTPOSTAGS)

      if foundPrep:
        # if term in self.invIndList:
        #   print("Matched docs for term '{}' are ({}) {}".format(term,len(self.invIndList[term]),self.invIndList[term]))
        # else:
        #   print("  '{}' not found".format(term))
        if cond:
          matchingDocs |= self.invIndList[term]
        # else:
        #   print("  '{}' is ignored".format(term))
      elif TAG[1] == 'IN':
        foundPrep = 1
        # print("{} term first IN".format(term_))
    return matchingDocs

  def vocab_size(self):
    temp = list(self.actualTermFreq.items())
    # temp = list(self.invIndList.items())
    # temp = [[term[0],len(term[1])] for term in temp]
    temp.sort(key=lambda x: x[1],reverse=True)
    count = 0
    print("Total terms in doc:",len(temp))
    for term in temp:
      if term[1] > self.freqThres:
        count += 1
    print("Num of Stop words:", count)
    return len(self.invIndList.keys())-count

  def plotFrequency(self, cutoff=None):
      if(not cutoff):
        cutoff = len(self.invIndList)
      
      termsToPlot = sorted(self.invIndList.items(), key = lambda z: len(z[1]), reverse = True)[0:cutoff]

      plt.figure(figsize=(0.4*cutoff, 6))
      plt.bar([x[0] for x in termsToPlot], [x[1][0] for x in termsToPlot])
      plt.xlabel("Terms") 
      plt.ylabel("Frequency") 
      plt.title("Term Frequency Plot") 
      plt.setp(plt.axes().get_xticklabels(), rotation=45, horizontalalignment='right')
      plt.show() 
 
#Can optimize union operations....

Ifull = InvertedIndex(data.docs)
Fp, Fr, Fret = data.executeQueries(Ifull)
Ifull.vocab_size()

"""**Task 2 & 3**

**Ir Index**

In Ifull model, as we saw, a large number of documents were getting retrieved. For building a better information retrieval model, we need to give user more relevant queries in lesser retrieved documents. So we will attempt to decrease the number of retrieved documents while keeping recall high.

First processing : Removal of stopwords
Index size will reduce as we remove stopwords from both queries and corpora. The stopwords are composed of the terms which occur most frequently across all the documents of the corpora. For example, if a term abcd is present 4 times in document A and 2 times in document B then the frequency of occurence of term abcd will be 6 which will be considered while finding out stopwords.

Number of stopwords removed = (number of words with frequency higher than 9) 

This frequency threshold is an ideal choice because even though we can get 100% recall at higher thresholds, that will cause the number of retrieved documents to increase a lot.

At the current frequency threshold, the average number of retrieved documents across all queries is half than that of Ifull model, even while recall is maintained high.


Second processing : Applying stemming on 
Stopwords + Porter Stemmer
Again, index size will further reduce as multiple variations of a word will be converted and mapped to a single term.

Example -
	The word 'circuit' is present in 37 docs
	The word 'circuits' is present in 34 docs
	Number of docs containing both the terms (intersection) is 15.
	Number of docs containing atleast one of the terms (union) is 56.
	The word 'circuits' will be modified to 'circuit' everywhere in the corpora as well as index. Hence the index size decreases.

	Query 2 is "INFORMATION ON DESIGN OF TIME DIVISION MULTIPLEXING CIRCUITS"
	Number of relevant retrieved documents before stemming - 6
	Number of relevant retrieved documents after stemming - 7


By using this pipeline, i.e. first stopword removal then stemming, we avoid the need for undergoing stemming on words that may later be removed because they are also in the stopword list.
"""

Ir = InvertedIndex(data.docs,['SW','STEM'],55)
Rp, Rr, Rret = data.executeQueries(Ir)
Ir.vocab_size()
data.plotComp(Fr,Rr,'R','IFull','IR')

"""**Iprecision**

Iprecision

There are two models here for consideration.

Ip1

1)  Removal of Stopwords 
    Index size decreases due to removal of frequent words in the index. We ended up removing all terms with more than 10 frequency in the corpora.
    This leads to an increase in precision as common words that retreive a lot of documents aren't being used to retreive docs.
    Number of stopwords removed = 76

2)  Query Processing Using Part-Of-Speech Tagging

    Looking at the queries we can see that the initial terms of all queries are trivial words, i.e. not relevant to the the docs to be retrieved. 
    So we will remove the initial trivial terms from queries till the first prepositon. This allows us to remove all irrelevant part-of-speech terms that retrieve extra documents.
    This gives a rise to precision as the docs which were getting returned because of the trivial terms will no longer be retrieved. 

    [('information', 'NN'), ('on', 'IN'), ('high', 'JJ'), ('current', 'JJ'), ('transistor', 'NN'), ('switches', 'NNS')]
    [('information', 'NN'), ('on', 'IN'), ('design', 'NN'), ('of', 'IN'), ('time', 'NN'), ('division', 'NN'), ('multiplexing', 'VBG'), ('circuits', 'NNS')]
    [('details', 'NNS'), ('of', 'IN'), ('available', 'JJ'), ('low', 'JJ'), ('voltage', 'NN'), ('capacitors', 'NNS')]

    The above reduction of queries into their POS TAGS show that the prepositions mark the relevance start of a query.

Ip2

1)  Removal of stopwords
    On a similar note removal of stopwords leads to an increase in precision
    Number of stopwords removed = 64  

2)  Lemmatization
    Lemmatization reduced the words in the corpora to their root form. This increased the precision as it helped various word forms of the same word to be converted into a similar form.
"""

Ip1 = InvertedIndex(data.docs,['PREPO','SW'],10)
P1p, P1r, P1ret = data.executeQueries(Ip1)
Ip1.vocab_size()
data.plotComp(Fp,P1p,'P','IFull','IP1')

Ip2 = InvertedIndex(data.docs,['SW','LEM'],13)
P2p, P2r, P2ret = data.executeQueries(Ip2)
Ip2.vocab_size()
data.plotComp(Fp,P2p,'P','IFull','IP2')

print("Graph 1")
data.plotComp(P1p,Rp,'P','IP1','IR')
print("Graph 2")
data.plotComp(P2p,Rp,'P','IP2','IR')
print("Graph 3")
data.plotComp(P1r,Rr,'R','IP1','IR')
print("Graph 4")
data.plotComp(P2r,Rr,'R','IP2','IR')

"""i. Precision has been successfully boosted in Ip over Ifull.
We see that stopword removal, lemmatization and query processing lead to increased precision.

ii. Recall has been maintained high in Ir.
However number of retrieved documents have beein significantly reduced. 
We see that stopword removal and stemming lead us to have greater number of relevant retrieved documents in lesser number of retrieved documents.

iii. Both graph1 and graph2 show higher precision of Ip1 and Ip2 over majority of queries than Ir. Similarly, Ir shows overall greater recall than Ip1 and Ip2 in graph3 and graph4.
"""



"""**TASK 4**"""

new_queries = ['I*ION ON HIGH *ENT TRANSISTOR SWI*',
 'INF* ON DESIGN OF TIME D*ION *ING CIRCUITS',
 '*LS OF AV*IBLE LOW VO* CAPACITORS',
 'DESIGN OF DIRECT C*ED FLIP FLOPS TO FU* WITH THE *UM VARIATIONS IN THE VALUES OF THE CIRCUIT COMPONENTS',
 'PLEASE SUPPLY INFORMATION ON THE PER* OF TYPICAL MA* FILM MEMORY SYSTEMS WITH CIRCUIT DIAGRAMS',
 'I WOULD LIKE *S OF THE WORK WH*H HAS BEEN DONE TO EXTEND THE FREQUENCY RANGE OF MAGNETIC AMPLIFIERS',
 'I WOULD LIKE *TION ON THE RA* OF STATIC RELA*YS SUITABLE FOR USE AT HIGH SWITCHING RATES',
 'I AM INTERESTED IN CIRCUI* CAPABLE OF GEN* EXTREMELY NARROW PULSES',
 'PLEASE SUPPLY INFORMATION ON THE THEORY AND USE OF PARAMETRIC AMPLIFIERS',
 'THE SYNTHESIS OF NET* WITH GIVEN *A D*A TRANSFER FUNCTIONS']
data.queries = new_queries

class BigramIndex(object):
  def __init__(self, InvInd):
    self.InvInd = InvInd
    self.bigramList = dict()
    for term in self.InvInd.actualTerms:
      newterm = '$'+term+'$'
      for i in range(len(newterm)-1):
        bigram = newterm[i:i+2]
        if bigram not in self.bigramList:
          self.bigramList[bigram]={term}
        elif term not in self.bigramList[bigram]:
          self.bigramList[bigram].add(term)

  def isCorrectTerm(self, phrase, possibleTerm):
    phrase = '$'+phrase+'$'
    possibleTerm = '$'+possibleTerm+'$'
    parts = phrase.split('*')
    i=0
    for p in parts:
      v = possibleTerm[i:].find(p)
      if v == -1:
        return False
      i += len(p)
    return True

  def queryGetMatchingTerms(self, phrase):
    matchingTerms = set()
    isFirst = 1
    newphrase = '$'+phrase+'$'
    
    for i in range(len(newphrase)-1):
      bigram = newphrase[i:i+2]
      if '*' in bigram:
        continue
      elif bigram in self.bigramList:
        if isFirst:
          matchingTerms = set(self.bigramList[bigram])
          isFirst = 0
        else:
          matchingTerms &= self.bigramList[bigram]
      else:
        # print("Bigram '{}' not found in Index List".format(bigram))
        return set()
    
    matchingTerms = set(term for term in matchingTerms if self.isCorrectTerm(phrase, term))
    # print("Terms for phrase '{}' are ({}) {}".format(phrase, len(matchingTerms), matchingTerms))
    # print("xxx",matchingTerms)
    return matchingTerms
 
  def queryGetAllMatchingTerms(self, completeQuery):
    phrases = completeQuery.split(' ')
    matchingTerms = set()
    for phrase in phrases:
      matchingTerms |= self.queryGetMatchingTerms(phrase)
    # print("yy",matchingTerms)
    return matchingTerms
 
  def queryGetMatchingDocs(self, completeQuery):  #Not tested yet
    matchingTerms = self.queryGetAllMatchingTerms(completeQuery)
    # print("zzz", matchingTerms)
    return self.InvInd.queryGetMatchingDocs(matchingTerms)

bi_Ifull= BigramIndex(Ifull)
temp = data.executeQueriesBi(bi_Ifull)

bi_Ir = BigramIndex(Ir)
temp = data.executeQueriesBi(bi_Ir)



bi_Ip = BigramIndex(Ip2)
temp = data.executeQueriesBi(bi_Ip)



"""Constructed a bigram index list for the terms present in the actual docs.

For every wildcard query we take the term and find possible other terms for it. We then use the same constructed index list to get the relevant doc ids.

For the query: I*ION ON HIGH  *ENT TRANSISTOR SWI *

Possilbe terms found by the bigram index model for the term " *ENT" are measurement, experiment, present, ambient, etc.

Because of this we get a lot of new irrevelant terms which will decreases precision and increases recall.

We can see from the above cells that indeed the recall values has increased and precision values has reduced.
"""
