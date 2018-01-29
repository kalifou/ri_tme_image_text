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

# model_type = Vectoriel | Okapi | Language | PageRank | Hits | MetaModel
if __name__ == "__main__":
    t1 = time.time()
    K = 20 #21 best cluster nb found with exp 1
    N = 36 #36 maximizes CR, found with exp 2
    fname = "easyCLEF08/easyCLEF08_text.txt"
    query_file = "easyCLEF08/easyCLEF08_query.txt"
    relevance_file = "easyCLEF08/easyCLEF08_gt.txt"
    type = "Greedy_diversity_euclidian"
    baseline_type ="Euclidian_model"
    
    
    #compute baseline
    eval_platform = EvalIRModel(N,fname,query_file,relevance_file,model_type=baseline_type,div_K=K,div_N=N,eval_N=20)
    models_prec, models_cr, models_AP = eval_platform.eval_std()
    baseline_CR = models_cr[baseline_type]
    baseline_PR = models_prec[baseline_type]
    
    #experience 1: Study the impact of the number of considered documents 
    #for accuracy and diversity
    
#    Ns = np.arange(0,50,1) #np.arange(25,65,1)
#    CRs = []
#    PRs = []
#    for N in Ns:
#        eval_platform = EvalIRModel(N,fname,query_file,relevance_file,model_type=type,div_K=0.7,div_N=N,eval_N=50)
#        models_prec, models_cr, models_AP = eval_platform.eval_std()
#        CRs.append(models_cr[type])
#        PRs.append(models_prec[type])
#    
#    plt.figure(3)
#    plt.plot(Ns,[baseline_CR for i in range(len(Ns))])
#    plt.plot(Ns,CRs)
#    plt.legend(['CR20 baseline','CR20'], loc='lower right')
#    plt.xlabel('number of ranked docs selected for clustering')
#    plt.savefig('impact_of_selected_docs_for_clustering_K=20_CR_cluster_size.jpg')
#    plt.show()
#    
#    plt.figure(4)
#    plt.plot(Ns,[baseline_PR for i in range(len(Ns))])
#    plt.plot(Ns,PRs)
#    plt.legend(['PR20 baseline','PR20'], loc='lower right')
#    plt.xlabel('number of ranked docs selected for clustering')
#    plt.savefig('impact_of_selected_docs_for_clustering_K=20_PR_cluster_size.jpg')
#    plt.show()
#    print "Exec duration(s) : ",time.time()-t1
    
    
    #experience 2: Study the impact of alpha for accuracy and diversity
    alphas = np.arange(0,1.1,0.2) #05)
    CRs = []
    PRs = []
    for alpha in alphas:
        eval_platform = EvalIRModel(50,fname,query_file,relevance_file,model_type=type,div_K=alpha,div_N=50,eval_N=20)
        models_prec, models_cr, models_AP = eval_platform.eval_std()
        CRs.append(models_cr[type])
        PRs.append(models_prec[type])
    
    plt.figure(3)
    plt.plot(alphas[:-1],[baseline_CR for i in range(len(alphas[:-1]))])
    plt.plot(alphas[:-1],CRs[:-1])
    plt.legend(['CR20 baseline','CR20'], loc='lower right')
    plt.xlabel('alpha')
    plt.savefig('alpha_dissim_CR.jpg')
    plt.show()
    
    plt.figure(4)
    plt.plot(alphas[:-1],[baseline_PR for i in range(len(alphas[:-1]))])
    plt.plot(alphas[:-1],PRs[:-1])
    plt.legend(['PR20 baseline','PR20'], loc='lower right')
    plt.xlabel('alpha')
    plt.savefig('alpha_dissim_PR.jpg')
    plt.show()
    print "Exec duration(s) : ",time.time()-t1