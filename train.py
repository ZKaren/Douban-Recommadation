# -*- coding: utf-8 -*-
from gensim.models import word2vec
import logging,csv,re
import pandas as pd
import numpy as np
def make_txt(infile,outfile): #输入所有书籍信息 输出语料库  共65726本书 512090个标签
    table=pd.read_csv(r'F:\data\douban\results2.csv',header=None)
    table=table.drop_duplicates()
    count=0
    with open(outfile,'a+',encoding='utf-8') as w:
        for i in range(len(table)):
            try:
                item=table.loc[i,6]
                item=item[1:len(item)-1]
                tags=item.split(',')
                for tag in tags:
                    tag=tag.strip()
                    tag=tag[1:len(tag)-1]
                    w.write(tag)
                    count=count+1
                    w.write(' ')
            except:
                pass
def train(infile,outfile):  #输入标签文件，训练语料库
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)  
    sentences =word2vec.Text8Corpus(infile)  # 加载语料  
    model =word2vec.Word2Vec(sentences, size=100,min_count=0)  #训练skip-gram模型，默认window=5 
    model.save(outfile)
    return model            

def tag_vec(model,infile,outfile):
    label=[]
    table=pd.read_csv(r'F:\data\douban\results2.csv',header=None)
    table=table.drop_duplicates()
    with open(outfile,'a+',encoding='utf-8',newline='') as csvwriter:
        w=csv.writer(csvwriter)
        for i in range(len(table)):
            try:
                tags=table.loc[i,6]
                tags=tags[1:len(tags)-1]
                tags=tags.split(',')
                for tag in tags: 
                    try:
                        tag=tag.strip()
                        tag=tag[1:len(tag)-1]
                        if tag not in label:
                            label.append(tag)
                            info=[]
                            info.append(tag)
                            #print(model[tag])
                            for num in list(model[tag]):
                                info.append(num)
                            w.writerow(info)  
                    except:
                        print('error')
                        pass
            except:
                print('error')
                pass
def makebookvec(infile,model):
    book_vec={}
    table=pd.read_csv(r'F:\data\douban\results2.csv',header=None)
    table=table.drop_duplicates()
    for i in range(len(table)):
        idnum=table.loc[i,0]
        tags=table.loc[i,6]
        book=np.zeros(100)
        tags=tags[1:len(tags)-1]
        tags=tags.split(',')
        for tag in tags: #加总向量
            try:
                tag=tag.strip()
                tag=tag[1:len(tag)-1]
                book=book+model[tag]
            except:
                pass
        book_vec[idnum]=book
    return book_vec

if __name__=='__main__':
    tablefile=r'F:\data\douban\results2.csv'
    totrainfile=r'F:\data\douban\totrain.txt'
    trainedfile=r'F:\data\douban\trained.model'
    tagvecfile=r'F:\data\douban\tag_vec.csv'
    bookvecfile=r'F:\data\douban\book_vec.csv'
    make_txt(tablefile,totrainfile)
    model=train(totrainfile,trainedfile)
    tag_vec(model,tablefile,tagvecfile)
    book_vec=makebookvec(tablefile,model)
    with open(bookvecfile,'a+',encoding='utf-8',newline='') as csvwriter:
        w=csv.writer(csvwriter)
        for key,value in book_vec.items():
            info=[]
            info.append(key)
            for num in list(value):
                info.append(num)
            w.writerow(info)
    