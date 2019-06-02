#!/usr/bin/env python
# coding: utf-8
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
import urllib.request
import bs4
import argparse
from newspaper import Article
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

def url_to_text(url):
    req  = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = BeautifulSoup(html, 'lxml')
    type(soup)
    bs4.BeautifulSoup
    # title = soup.title
    f = open("content.txt", "w")
    all_para = soup.find_all("p")

    for para in all_para:
        f.write(' ' + str(para.get_text()))
        # print(para.get_text())
    # generate_summary("content.txt", 2)
    return "content.txt"

def read_article(file_name):
    file = open(file_name, "r")
    filedata = file.readlines()
    article = filedata[0].split(". ")
    sentences = []

    for sentence in article:
        # print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop() 
    
    # print(sentences)
    return sentences

# read_article("content.txt")

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(file_name, top_n=5):
    try:
        nltk.download("stopwords")
        stop_words = stopwords.words('english')
        summarize_text = []

        # Step 1 - Read text anc split it
        sentences =  read_article(file_name)
        # print(sentences)
        # Step 2 - Generate Similary Martix across sentences
        sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

        # Step 3 - Rank sentences in similarity martix
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
        scores = nx.pagerank(sentence_similarity_graph)

        # Step 4 - Sort the rank and pick top sentences
        ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
        # print("Indexes of top ranked_sentence order are ", ranked_sentence)    

        for i in range(top_n):
            summarize_text.append(" ".join(ranked_sentence[i][1]))

        print (summarize_text)
        # Step 5 - Offcourse, output the summarize texr
        return summarize_text
    except:
        return " neha "

# let's begin
# generate_summary( "msft.txt", 2)
def convert_url_to_text(url):
    try:
        print(url)
        file_name = url_to_text(url)
        return file_name
    except:
        return " earring "

generate_summary("notes.txt",5)

# sentences =  read_article(file_name)
# nltk.download("stopwords")
# stop_words = stopwords.words('english')
# summarize_text = []
# sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)
# sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
# scores = nx.pagerank(sentence_similarity_graph)
# ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    
# for i in range(10):
#       summarize_text.append(" ".join(ranked_sentence[i][1]))
# print("Summarize Text: \n", ". ".join(summarize_text))