# -*- coding: utf-8 -*-
from Index import Index
from ParserCLEF08 import ParserCLEF08
from TextRepresenter import PorterStemmer
from Weighter import Binary, TF, TF_IDF, Log, Log_plus
from EvalMeasure import EvalIRModel
import numpy as np
import os.path
import time
import matplotlib.pyplot as plt

if __name__ == "__main__":
    t1 = time.time()
    K = 20 #21 best cluster nb found with exp 1
    N = 36 #36 maximizes CR, found with exp 2
    fname = "easyCLEF08/easyCLEF08_text.txt"
    query_file = "easyCLEF08/easyCLEF08_query.txt"
    relevance_file = "easyCLEF08/easyCLEF08_gt.txt"
    type = "KMeans_diversity" # model_type = Vectoriel | Okapi | Language | PageRank | Hits | MetaModel
    baseline_type = "Language"
    
    
    #compute baseline
    eval_platform = EvalIRModel(N,fname,query_file,relevance_file,model_type=baseline_type,div_K=K,div_N=N,eval_N=20)
    models_prec, models_cr, models_AP = eval_platform.eval_std()
    baseline_CR = models_cr[baseline_type]
    baseline_PR = models_prec[baseline_type]
    
    '''
    #experience 1: Study the impact of cluster number for accuracy and diversity
    Ks = np.arange(1,37,1)
    CRs = []
    PRs = []
    for K in Ks:
        eval_platform = EvalIRModel(N,fname,query_file,relevance_file,model_type=type,div_K=K,div_N=N,eval_N=20)
        models_prec, models_cr, models_AP = eval_platform.eval_std()
        CRs.append(models_cr[type])
        PRs.append(models_prec[type])
    
    plt.figure(1)
    plt.plot(Ks,[baseline_CR for i in range(len(Ks))])
    plt.plot(Ks,CRs)
    plt.legend(['CR20 baseline','CR20'], loc='lower right')
    plt.xlabel('number of clusters')
    plt.savefig('impact_of_clusters_N=36_CR_cluster_rank.jpg')
    plt.show()
    
    plt.figure(2)
    plt.plot(Ks,[baseline_PR for i in range(len(Ks))])
    plt.plot(Ks,PRs)
    plt.legend(['PR20 baseline','PR20'], loc='lower right')
    plt.xlabel('number of clusters')
    plt.savefig('impact_of_clusters_N=36_PR_cluster_rank.jpg')
    plt.show()
    print "Exec duration(s) : ",time.time()-t1
    '''
    #experience 2: Study the impact of the number of considered documents when clustering (N)
    #for accuracy and diversity
    
    Ns = np.arange(25,101,1)
    CRs = []
    PRs = []
    for N in Ns:
        eval_platform = EvalIRModel(N,fname,query_file,relevance_file,model_type=type,div_K=K,div_N=N,eval_N=20)
        models_prec, models_cr, models_AP = eval_platform.eval_std()
        CRs.append(models_cr[type])
        PRs.append(models_prec[type])
    
    plt.figure(3)
    plt.plot(Ns,[baseline_CR for i in range(len(Ns))])
    plt.plot(Ns,CRs)
    plt.legend(['CR20 baseline','CR20'], loc='lower right')
    plt.xlabel('number of ranked docs selected for clustering')
    plt.savefig('impact_of_selected_docs_for_clustering_K=20_CR_cluster_size.jpg')
    plt.show()
    
    plt.figure(4)
    plt.plot(Ns,[baseline_PR for i in range(len(Ns))])
    plt.plot(Ns,PRs)
    plt.legend(['PR20 baseline','PR20'], loc='lower right')
    plt.xlabel('number of ranked docs selected for clustering')
    plt.savefig('impact_of_selected_docs_for_clustering_K=20_PR_cluster_size.jpg')
    plt.show()
    print "Exec duration(s) : ",time.time()-t1
    
