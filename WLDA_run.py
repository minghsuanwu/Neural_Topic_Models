#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   WLDA_run.py
@Time    :   2020/10/04 21:03:13
@Author  :   Leilan Zhang
@Version :   1.0
@Contact :   zhangleilan@gmail.com
@Desc    :   None
'''




import os
import re
import torch
import pickle
import argparse
import logging
from models import WLDA
from utils import *
from dataset import DocDataset
from multiprocessing import cpu_count

parser = argparse.ArgumentParser('GSM topic model')
parser.add_argument('--taskname',type=str,default='cnews10k',help='Taskname e.g cnews10k')
parser.add_argument('--no_below',type=int,default=5,help='The lower bound of count for words to keep, e.g 10')
parser.add_argument('--no_above',type=float,default=0.005,help='The ratio of upper bound of count for words to keep, e.g 0.3')
parser.add_argument('--num_epochs',type=int,default=100,help='Number of iterations (set to 100 as default, but 1000+ is recommended.)')
parser.add_argument('--n_topic',type=int,default=20,help='Num of topics')
parser.add_argument('--bkpt_continue',type=bool,default=False,help='Whether to load a trained model as initialization and continue training.')
parser.add_argument('--use_tfidf',type=bool,default=False,help='Whether to use the tfidf feature for the BOW input')
parser.add_argument('--rebuild',type=bool,default=True,help='Whether to rebuild the corpus, such as tokenization, build dict etc.(default True)')
parser.add_argument('--dist',type=str,default='gmm_std',help='Prior distribution for latent vectors: (dirichlet,gmm_std,gmm_ctm,gaussian etc.)')
parser.add_argument('--batch_size',type=int,default=512,help='Batch size (default=512)')
args = parser.parse_args()


def main():
    global args
    taskname = args.taskname
    no_below = args.no_below
    no_above = args.no_above
    num_epochs = args.num_epochs
    n_topic = args.n_topic
    n_cpu = cpu_count()-2 if cpu_count()>2 else 2
    bkpt_continue = args.bkpt_continue
    use_tfidf = args.use_tfidf
    rebuild = args.rebuild
    dist = args.dist 
    batch_size = args.batch_size

    device = torch.device('cuda')
    docSet = DocDataset(taskname,no_below=no_below,no_above=no_above,rebuild=rebuild,use_tfidf=False)
    voc_size = docSet.vocabsize
    print('voc size:',voc_size)
    n_topic = args.n_topic
    model = WLDA(bow_dim=voc_size,n_topic=n_topic,device=device,dist=dist,taskname=taskname,dropout=0.4)
    model.train(train_data=docSet,batch_size=batch_size,test_data=docSet,num_epochs=num_epochs,log_every=10,beta=1.0)
    model.evaluate(test_data=docSet)


if __name__ == "__main__":
    main()