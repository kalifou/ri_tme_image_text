# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 22:32:40 2017

@author: kalifou
"""
import numpy as np
from Index import Index
    
def max_K(list,K):
    """
    returning at most the first K elements of the list
    """
    l = len(list)
    res = list
    if l > K:
        res = list[:K] 
    return res

def get_Pre_Succ_seeds(Seeds, K, I):
    """returns Succ & Prec"""
    
    seed_ids = [int(elt[0]) for elt  in Seeds]
    Docs_id_ = set(seed_ids)  
    
    for id in seed_ids:
        #print "type err :",type(id)
        Docs_id_.update(I.getLinksForDoc(str(id)))
    
    Docs_id = [int(e) for e  in list(Docs_id_)]
    N_pgs = len(Docs_id)
    Index_P = { id:idx for idx,id in enumerate(Docs_id)}
    Counter_Index_P = { idx:id for idx,id in enumerate(Docs_id)}
    
    #print "Index P :",Index_P,"\n\n\n Counter IDX: ",Counter_Index_P    
    
    print "\nBuilding Pi..."
    Succ = { Index_P[p]:( I.getLinksForDoc(str(p)),len(I.getLinksForDoc(str(p)))) for p in Docs_id }
    P = {}
    succ_keys = list(Succ.keys())
    for e in Succ: #succ_keys:
        succ_e,l_e = Succ[e]
        for s in succ_e:    
            if Index_P.get(int(s),"Unknown_Doc_id") not in P:
                #Index_P[int(s)] = len(Index_P)+1
                #Counter_Index_P[len(Index_P)+1]=int(s)
                P[Index_P.get(int(s),"Unknown_Doc_id")] = set()
                #Docs_id.append(int(s))
                #P[Index_P[s]] = set()
            P[Index_P.get(int(s),"Unknown_Doc_id")].add(e) 
            #P[Index_P[s]] = set()
    for key_p in P.keys():
        P[key_p] = max_K(list(P[key_p]),K)
        
    
    #Succ = { Index_P[p]:( I.getLinksForDoc(str(p)),len(I.getLinksForDoc(str(p)))) for p in Docs_id }
    #N_pgs = len(Docs_id)
    #print P
    return P,Succ,Index_P,Counter_Index_P,N_pgs

def get_A(P,Succ,N_pgs):
    print "Building Matrix A..."
    A = np.zeros((N_pgs,N_pgs))
    for i in range(N_pgs):
        for j in range(N_pgs):
            Pi= P.get(i,[])
            Succ_j,lj = Succ .get(j,([],-1)) 
            
            if lj==0:  #j is isolated
                A[i][j] = 1./N_pgs
                
            elif j in Pi: # j precedes i
                #print 'happpens'
                A[i][j] = 1./lj                
    return A

def select_G_q( n, k, query, model,I):
    """
    params :    
    n : number of seed documents
    k : number of entering links to consider for the seeds
    query : query the graph is being built for 
    model : model to select the seeds relevant for the input query
    """
    
    # Selecting the scores of docs with respect to the query
    docs_scores = model.getScores(query)
    # Ordering the docs by descending scores (D,score)
    desc_dcs_scores = sorted(docs_scores.iteritems(), key=lambda (k,v): (v,k),reverse=True)
    # Selecting n best seeds 
    seeds = max_K(desc_dcs_scores,n)
    
    # Building the graph using these seeds & parameter k (max number of entering links to consider)
    return get_Pre_Succ_seeds(seeds, k,I)

class RandomWalk(object):
    def __init__(self,index,N_pgs):
        self.index = index
        self.N_pages = N_pgs


    def randomWalk(self):
        raise NotImplementedError('Always abstract class') 
        
    
class PageRank(RandomWalk):
    
    def __init__(self,N_pages, d):
        """
        d : proba to randomly click on a link/page
        N_pages : Number of Web pages
        index : contains 
        P : {j from V | j->i  from E}
        """
        self.d = d
        self.N_pages = N_pages
        self.eps = 1e-1
        
    def randomWalk(self, A):
        
        self.mu = np.zeros((self.N_pages,1)) + 1./self.N_pages 
        # indices : position dans la le graphe        
        
        sum = 1.
        cpt=0
        while(sum > self.eps):
            prec = self.mu
            self.mu = ((1.-self.d)/self.N_pages) + self.d * np.dot(A,self.mu )
            sum = np.sum(abs(self.mu-prec))
            print "Step : ",cpt,", Sum of abs. error (mu) : ",sum
            cpt+=1
        print "...Converged!"
        
    def get_result(self,Counter_Index):
        r = { int(Counter_Index[k]): self.mu[k] for k in range(len(self.mu)) }
        return r

class Hits(RandomWalk):
    """
    descr...
    """
    def __init__(self,N_pages, N_iters=10):
        self.N_pages = N_pages
        self.N_iters = N_iters
        
    def randomWalk(self, P_m, Succ_m, Index_P):
        """descr...
        """
        # Authority nodes a
        self.a = np.ones(self.N_pages)
        # Hub nods h
        self.h = np.ones(self.N_pages) 

        for t in range(self.N_iters):
            #print " iter t :",t
            for i in range(self.N_pages):
                Js = P_m.get(i,[])
                
                if Js != []:
                    sj= 0.
                    for j in Js: # j -> i
                        sj += self.h[j]
                    self.a[i] = sj
                    
                else:
                    pass                
                #print "viz :",Succ_m.get(i,([],0))
                Succ_i,l_i = Succ_m.get(i,([],0))
                if Succ_i != []:
                    sj = 0.
                    for j in Succ_i: # i -> j              
                        idx = Index_P.get(j,"Unknown_Doc_id")
                        #print "idx :",idx
                        if (j != '') and ("." not in j) and (idx != "Unknown_Doc_id"):
                            sj += self.a[idx]
                    self.h[i] = sj
                else: 
                    pass
                
            # 2-Normalizing a & h
            self.a = self.a / np.linalg.norm(self.a,2)
            self.h = self.h / np.linalg.norm(self.h,2)
            
        print "As :",self.a[1:10]
        print "Hs :",self.h[1:10]
    
    def get_result(self,Counter_Index):
        r = { int(Counter_Index[k]): self.a[k] for k in range(len(self.a)) }
        return r
    