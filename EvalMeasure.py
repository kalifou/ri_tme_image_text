# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 14:20:28 2017

@author: kalifou
"""
import numpy as np
import sys
import matplotlib.pyplot as plt
from Weighter import Binary, TF, TF_IDF, Log, Log_plus
from IRmodel import Vectoriel, Okapi, LanguageModel, RankModel, HitsModel, MetaModel, KMeans_diversity, Greedy_diversity, Greedy_diversity_euclidian,Euclidian_model
from ParserCLEF08 import ParserCLEF08
from TextRepresenter import PorterStemmer
from collections import defaultdict
from Index import Index
from GroundTruthParser import GroundTruthParser
import os.path
import pickle
from Featurer import FeaturerModel,FeaturerList

def intersection(l1,l2):
    """Intersection between list l1 & l2"""
    if len(l1) == 0:
        print "l1 is empty !"
    assert(isinstance(l1[0],int))
    assert(isinstance(l2[0],int))
    return list(set(l1).intersection(l2))


def removeUnknownStems(Query,Index):
    """Remove unknown stem from query tf"""
    removed_stems = ""
    query_tf = Query.getTf()
    for stem in query_tf.keys():
        #if unknown stem remove from query
        if not Index.stems.has_key(stem):
                removed_stems += " " + stem + " "
                query_tf.pop(stem)
    #if len(removed_stems) > 0:
        #print "Unknown stems: " + removed_stems

def initIndex(database_file):
    """Init Index or load it if previously computed"""
    sys.stdout.write("Indexing database...")
    sys.stdout.flush()
    if os.path.isfile('Index.p'):
       I = pickle.load( open( "Index.p", "rb" ) ) 
    
    else:
        parser = ParserCLEF08()
        textRepresenter = PorterStemmer()
        I = Index(parser,textRepresenter)
        I.indexation(database_file)
        I.parser = None
        pickle.dump( I, open( "Index.p", "wb" ) )
        
    sys.stdout.write("Done!\n")
    sys.stdout.flush()
    
    return I

def initModels(I,modelType):
    """Init Models of type modelType or load if already computed"""
    
    model_file_name = modelType + '.p'
    
    sys.stdout.write("Creating models...")
    sys.stdout.flush()
    
    if os.path.isfile(model_file_name):
        models = pickle.load( open( model_file_name, "rb" ) )
        
    elif modelType == "Vectoriel":
        weighters =  [Binary(I), TF(I), TF_IDF(I), Log(I), Log_plus(I)]
        models = [Vectoriel(Index,True, w) for w in weighters]
        pickle.dump( models, open( model_file_name, "wb" ) )
    
    else:
        print "Unknown model type ABORT THE MISSION"
    
    sys.stdout.write("Done!\n")
    
    return models
        
class EvalMeasure(object):
    """Abstract class for query evaluation""" 
    def __init__(self):
        pass
    
    def evaluation(self, Query, retrieved_doc):
        """ Evaluate the list l of docs"""
        pass
    
    def getNumRecall(self, relevant_doc, retrieved_doc):
        """Compute recall for given query and sorted (document, score) list"""
        #print "Relevant : ", relevant_doc
        #print "\n\nRetrived : ", retrieved_doc,'\n\n'
        #print "intersect : ", intersection(relevant_doc,retrieved_doc),'\n\n'
        return float(len(intersection(relevant_doc,retrieved_doc)))
    

class Eval_P_N(EvalMeasure):
    """Class for query evaluation using precision-recall""" 
    def __init__(self,N):
        self.N=N
        
    def evaluation(self, Query, retrieved_doc):
        
        relevant_doc = np.array(Query.getRelevantDocs())[:,0]              
        retrieved = np.array( retrieved_doc ,dtype=int)[:,0][:self.N]        
        numerator = self.getNumRecall(relevant_doc, retrieved)
        return  numerator /self.N # simple precision meas.

class Eval_CR_N(EvalMeasure):
    """Class for query evaluation using precision-recall""" 
    def __init__(self,N):
        self.N=N
        
    def evaluation(self, Query, retrieved_doc):
        
        relevant_doc = np.array(Query.getRelevantDocs())[:,0]
        relevant_doc_subtopics = np.array(Query.getRelevantDocs())[:,2]
        #get all subpics from above
        
        top_N_retrieved = np.array( retrieved_doc ,dtype=int)[:,0][:self.N]
        retrieved_subtopics = set()
        
        found_docs = intersection(relevant_doc,top_N_retrieved)
        for doc in found_docs:
            ind = np.where(relevant_doc == doc)[0][0]
            retrieved_subtopics.add(relevant_doc_subtopics[ind])
            
        return  len(retrieved_subtopics) / float(len(set(relevant_doc_subtopics)))

class Eval_AP(EvalMeasure):
    """Class for query evaluation using average precision-recall""" 
    def __init__(self):
        pass
    
    def evaluation(self, Query, retrieved_doc):
        relevant_doc = np.array(Query.getRelevantDocs())[:,0]
        
        if relevant_doc[0] == None: #NO RELEVANT DOC FOR QUERY
            return 1
        #print "EVAL AP"
        #print "relevant type : ",type(relevant_doc[0])
        #print "retrieved type : ",type(retrieved_doc[0][0])
        retrieved = np.array(retrieved_doc,dtype=int)[:,0]
        #print "retrieved after numpy type : ",type(retrieved[0])
        precisions = []
        #print "relevant docs: " + str(relevant_doc)
        for i,doc in enumerate(retrieved):
            
            #if current doc is relevant, add current precision
            if doc in relevant_doc:
                #print "doc relevant :" + str(doc)
                #print "i,retr,nmRecal :",i,retrieved,self.getNumRecall(relevant_doc, retrieved[0:i+1]) / (i+1.)
                
                precisions.append(self.getNumRecall(relevant_doc, retrieved[0:i+1]) / (i+1))
                
        #print "prec :",precisions
        #average precision
        return 0 if len(precisions) == 0 else np.mean(precisions)
 
class EvalIRModel(object):
    
    def plot_(self,recall, interpolated_prec,precision):
        """Plotting Both : simple & interpolated precision - recall curve"""
        fig = plt.figure() #(figsize=(9,7))
        fig.suptitle('Precision - Recall',fontsize=15)
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.plot(recall,precision, 'b-',label="precision")
        plt.plot(recall,interpolated_prec, 'r',label="interpolated precision")
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.show()
        
    def __init__(self, N, index_file, query_file, relevance_file,model_type="Vectoriel",div_K=None,div_N=None,eval_N=20):
        """ model_type = Vectoriel | Okapi | Language | PageRank | MetaModel """
        self.N= eval_N
        self.Index = initIndex(index_file)
        
        if model_type  == "Vectoriel":
            self.models = [Vectoriel(Index,True, Log_plus(self.Index))] #initModels(self.Index,model_type)
        elif model_type == "Euclidian_model":
            self.models = [Euclidian_model(self.Index,Log_plus(self.Index))]
            
        elif model_type == "Language":
            print "Init of Language model"
            self.models = [LanguageModel(self.Index,0.2)]
            
        elif model_type == "Okapi":
            self.models = [Okapi(self.Index)]
            
        elif model_type == "PageRank":
            self.models = [RankModel(self.Index)]
            
        elif model_type == "Hits":
            self.models = [HitsModel(self.Index)]
        
        elif model_type == "KMeans_diversity":
            self.models = [KMeans_diversity(self.Index,div_K,div_N)]
        
        elif model_type == "Greedy_diversity":
            self.models = [Greedy_diversity(self.Index,div_K,div_N)]
            
        elif model_type == "Greedy_diversity_euclidian":
            print "alpha, N:", div_K,div_N
            self.models = [Greedy_diversity_euclidian(self.Index,alpha=div_K, N=div_N)]
            
        elif model_type == "MetaModel":
            """Learning a linear combination of 4 models"""
            I = self.Index
            w1 = TF_IDF(I)
            model1 = Vectoriel(I,True, w1)
            w2 = Log_plus(I)
            model2 = Vectoriel(I,True, w2)
            #w3 = Log(I)
            #model3 = Vectoriel(I,True, w3)
            
            model3 = Okapi(I)
            
            f1 = FeaturerModel(I,model1)
            f2 = FeaturerModel(I,model2)
            f3 = FeaturerModel(I,model3)
            #f4 = FeaturerModel(I,model4)
            
            listFeaturers = FeaturerList([f1,f2,f3]) #,f4])
            metamodel = MetaModel(listFeaturers,I,query_file,relevance_file)
            metamodel.train()
            self.models = [metamodel]
            
        print type(self.models[0])    
        self.query_file = query_file
        self.relevance_file = relevance_file
        self.query_parser = GroundTruthParser(self.query_file, self.relevance_file)  
    
    def eval_std(self, verbose=True):  
        """ Evaluate the a set of query using a set of different Vector Models 
            Todo : calculate mean & std of each model on the whole query dataset
            DRAFT !
        """
        
        sys.stdout.write("Evaluation of our models ...")
        print '\n'
        Eval = Eval_P_N(self.N)
        Eval_CR = Eval_CR_N(self.N)
        EvalAP = Eval_AP()
        
        models_prec = defaultdict(float)
        models_AP = defaultdict(float)
        models_CR = defaultdict(float)
        
        
        for i,m in enumerate(self.models):

            m_name = m.getName()
            if verbose:
                print "\n\nModel : ", m_name
            
            query_result = 0
            query_nb = 0
            self.query_parser = GroundTruthParser(self.query_file, self.relevance_file)
            Q = self.query_parser.nextQuery()
            query_nb += 1.
            while (Q != -1):
                #print "hhh"
                #go to next query if no relevant document related to query
                if Q.getRelevantDocs()[0][0] == None:
                    #print "query ignored: no relevant docs"
                    Q = self.query_parser.nextQuery()
                    continue
                
                removeUnknownStems(Q, self.Index)
                #print "query results", query_result
                query_result = m.getRanking(Q.getTf())
                prec = Eval.evaluation(Q, query_result)
                #cr = 
                
                
                #accumulate results
                if not models_prec.has_key(m_name):
                    models_prec[m_name] = Eval.evaluation(Q, query_result)
                    models_CR[m_name] = Eval_CR.evaluation(Q, query_result)
                    models_AP[m_name] = EvalAP.evaluation(Q, query_result)
                else:
                    
                    models_prec[m_name] += np.array(prec)
                    models_CR[m_name] += Eval_CR.evaluation(Q, query_result)
                    models_AP[m_name] += EvalAP.evaluation(Q, query_result)

                Q = self.query_parser.nextQuery()
                query_nb += 1
            models_AP[m_name] = models_AP[m_name]/query_nb
            models_CR[m_name] = models_CR[m_name]/query_nb
            models_prec[m_name] = models_prec[m_name]/query_nb
                       
            if verbose:
                #self.plot_(models_recall[m_name], models_inter_prec[m_name], models_prec[m_name])
                print 'AP: ',  models_AP[m_name]
                print 'P@',self.N," : ",models_prec[m_name]
                print 'CR@',self.N," : ",models_CR[m_name]
            
        return models_prec, models_CR, models_AP
        
    def eval(self,N): 
        """ Ploting Interpolated Precision-recall for a set of models """
        
        sys.stdout.write("Evaluation of our models ...")
        print '\n'
        Eval = Eval_P_N(N)
        EvalCR = Eval_CR_N(N)
        EvalAP = Eval_AP()
        
        query_result = 0
        Q = self.query_parser.nextQuery()
        while (Q != -1):
            #go to next query if no relevant document related to query
            if Q.getRelevantDocs()[0][0] == None:
                #print "query ignored: no relevant docs"
                Q = self.query_parser.nextQuery()
                continue
            
            removeUnknownStems(Q, self.Index)
            for i,m in enumerate(self.models):
                print "\n\nModel : ", m.getName()
                print Q.getText() 

                query_result = m.getRanking(Q.getTf())
                precision = Eval.evaluation(Q, query_result)
                cr = Eval_CR_N.evaluation(Q, query_result)
                #Display first 10 values to see performances
                #print 'recall :', recall[0:10]
                #print 'precision : ',precision[0:10]
                #print 'inter_precision : ',interpolated_prec [0:10]
                print "P@",N," :",precision 
                print "CR@",N," :",cr
                average_precision = EvalAP.evaluation(Q, query_result)
                print 'AP: ', average_precision
            Q = self.query_parser.nextQuery()