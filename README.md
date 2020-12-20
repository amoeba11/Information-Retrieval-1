# Information-Retrieval-1

## Constructing Inverted Index, Applying Linguistic Models and Generating Bigram Index.

```
1. ir_1.py - code file
2. documents.txt - contains the documents 
3. query.txt - queries provided for the documents
4. relevance_assessment.txt - relevant documents for each query from query.txt file to calculate precision and recall recall metrics
```

In ir_1.py (code file) -

### Task 1 Inverted Index Construction

(a) Construct a full-text inverted index I f ull and display the size of vocabulary.

(b) Plot the dictionary terms in the decreasing order of their frequency in I f ull . Identify the stopwords in the corpora (if any) based on the size of the postings (not the standard lexicon of stopwords in nltk/spacy/online sources).

(c) Compute Precision and Recall for all 10 queries using I f ull . X axis shows the query ID and Y axis shows the performance score. Legends show the Precision and Recall scores.
White spaces are treated as logical OR operation.


### Task 2 
Select one or more linguistic models (text operations) and re-construct your inverted index; I P : to increase the precision and I R : to increase the recall.

(a) Report the changes in vocabulary size of I P and I R .

(b) Run the same set of queries used in Task 1 on the new revised inverted indices (I P and I R ) and report the precision and recall for each query. Display the results in form of a grouped bar plot for each query:
i. Precision results of I f ull and I P
ii. Recall results of I f ull and I R
iii. Precision and Recall results of I P and I R


### Task 3 
Give inferences and justification for the followings:
(a) the models selected in Task 2. If more than one linguistic models are used then why? and why only this pipeline should be used?

(b) the changes in the results of i, ii, and iii in Task 2b


### Task 4 
Generate a bi-gram index on I f ull , I P , and I R . Convert at least three words in each query to the following wildcard patterns: *X, X*, and X*Y. Example: This is a sample sentence can be converted to *is is a sa*ple sente*. Now, compute the precision and recall.
