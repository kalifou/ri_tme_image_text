# -*- coding: utf-8 -*-
from Index import Index
from ParserCLEF08 import ParserCLEF08
from TextRepresenter import PorterStemmer
from Weighter import Binary, TF, TF_IDF, Log, Log_plus
from EvalMeasure import EvalIRModel
import numpy as np
import os.path
import time

if __name__ == "__main__":
    t1 = time.time()
    N=20
    fname = "easyCLEF08/easyCLEF08_text.txt"
    query_file = "easyCLEF08/easyCLEF08_query.txt"
    relevance_file = "easyCLEF08/easyCLEF08_gt.txt"
    type = "KMeans_diversity" # model_type = Vectoriel | Okapi | Language | PageRank | Hits | MetaModel
    eval_platform = EvalIRModel(N,fname,query_file,relevance_file,model_type=type)
    simple_eval = False  
    
    if simple_eval :        
        eval_platform.eval(N)
    else:
        models_prec, models_cr, models_AP = eval_platform.eval_std()
    print "Exec duration(s) : ",time.time()-t1