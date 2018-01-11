# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 17:30:16 2017

@author: kalifou, portelas
"""
from TextRepresenter import PorterStemmer
#from ParserCACM import ParserCACM
from ParserCLEF08 import ParserCLEF08
import numpy as np

class GroundTruth(object):
    def __init__(self, query_id, doc_id, relevance, subtopic_id ):
        self.query_id = query_id  # ID of the current query       
        self.doc_id = doc_id 
        self.relevance = relevance
        self.subtopic_id = subtopic_id 
        
    def getId(self):
        return self.query_id
    
    def getDoc_id(self):
        return self.doc_id
    
    def getRelevance(self):
        return self.relevance
    
    def getSubtopic_id(self):
        return self.subtopic_id

class GroundTruthParser(object):
    """Class for query reading from file""" 
    def __init__(self, query_file, doc_file):
        self.query = open(query_file, 'r')
        self.textRepresenter = PorterStemmer()
        
        #init boolean to be able to close source files
        self.already_closed = False
        
        #Create parser to read query_file
        #WARNING WILL ONLY WORK ON CACM DATASET TODO FIND SOLUTION
        self.parser = ParserCLEF08()
        self.parser.initFile(query_file)
        
        #Build a dictionary (query_id, list of relevant documents) 
        self.relevant_docs = {}
        with open(relevance_file, 'r') as f:
            for line in f:
                data = line.split(" ")
                query_id = int(data[0])
                if(not self.relevant_docs.has_key(query_id)):
                    self.relevant_docs[query_id] = []
                #A list is added per relevant doc for later use of couple (themes, score) 
                self.relevant_docs.get(query_id).append([ int(data[1]), None, None])
                
    def nextQuery(self):
        """Return next Query object"""
        
        query_data = self.parser.nextDocument()
        
        if (query_data == None):
            if( not self.already_closed ):
                self.query.close()
                self.already_closed = True
                return -1
        
        query_id = query_data.getId()
        query_text = query_data.getText()
        query_tf = self.textRepresenter.getTextRepresentation(query_text)
        relevant_docs_to_query = np.array(self.relevant_docs.get(int(query_id),[[None,None,None]]))
        return Query(query_id, query_text, query_tf, relevant_docs_to_query)