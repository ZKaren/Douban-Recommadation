# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
class Heap():
    def __init__(self,heap):    #传入带key和value两个属性的双重列表
        self.heap=heap
    def modify_heap(self,position): #调整在特定位置上的小顶堆顶点
        l=len(self.heap)
        while(position*2+1<l):
            q=position*2+1
            if q<l-1:
                if self.heap[q][1]>self.heap[q+1][1]:  #q为cos值较小的记录的下标
                    q=q+1   
            if self.heap[position][1]>self.heap[q][1]:  #顶非最小则调换顺序
                swap=self.heap[position]
                self.heap[position]=self.heap[q]
                self.heap[q]=swap
                position=q
            else:
                break
        return self.heap
    def make_minheap(self):  #创建小顶堆
        l=len(self.heap)
        s=int(l/2)-1  #求得起始调整顶点
        while(s>=0):
            #print('调整顶点%d'%s)
            self.heap=self.modify_heap(s)
            s=s-1
        return self.heap
    def update_heap(self,data,position): #修改堆的数值，并使得堆自动调整为小顶堆
        if position>len(self.heap):
            print('overflow!')
            return self.heap
        self.heap[position]=data
        if position==0:
            self.modify_heap(0)
        else:
            self.make_minheap()
        return self.heap      
    def output_heap(self): #将小顶堆用升序以列表形式返回
        ordered_list=[]
        while(len(self.heap)!=0):
            ordered_list.append(self.heap[0])
            self.heap[0]=self.heap[len(self.heap)-1]   #最后一个元素置为第一个元素
            self.heap.pop()       #删除最后一个元素
            self.heap=self.modify_heap(0)  #重新排序
        return ordered_list
    
class Douban():  #豆瓣图书查询类，提供检索书籍并给出其相关书籍的接口
    def __init__(self):
        print('加载中，请稍候')
        self.bookvec={}   #书籍字典，Key为书籍id，Value为书籍向量
        self.book=pd.read_csv('bookinfo.csv',header=None)  #数据框存储书籍详细信息
        self.book=self.book.drop_duplicates()
        vec=pd.read_csv('bookvec.csv',header=None)
        vec=vec.drop_duplicates()
        for i in range(len(vec)):                        #将数据框转换为字典型
            self.bookvec[vec.loc[i,0]]=np.array(vec.loc[i,1:100])
        #print(self.book)
        print('加载完毕！')
    def getcos(self,a,b): #计算两向量之间余弦
        return a.dot(b.T)/(np.linalg.norm(a) * np.linalg.norm(b))
    def get_id(self,book_name): #输入书籍名称，返回书籍id
        result=self.book[self.book[1].isin([book_name])]
        #print(result)
        if len(result):         #若检索有结果，则返回书籍id
            result=result.reset_index(drop=True)
            id_num=result.loc[0,0]
            return id_num
        else:
            return -1           #无检索结果返回负值    
    def get_info(self,book_id):  #输入书籍id，返回书籍详细信息字典
        result=self.book[self.book[0].isin([book_id])]
        if len(result): 
            result=result.reset_index(drop=True)
            info=[]
            for i in range(6):
                info.append(result.loc[0,i])
            return info
        else:
            return []
    def find_near(self,book_id,num):  #输入一个书籍编号，运用堆排序top-k算法，寻找与其最接近的num本书  
        toheap=[]
        vec=self.bookvec[book_id]
        count=0
        for key,value in self.bookvec.items():
            if count<num:  #首先放入num个数据  
                if (key!=book_id):
                    info=[key,self.getcos(value,vec)]
                    toheap.append(info)
                    count=count+1
            elif count==num:  #调用Heap类将前num个数据生成小顶堆
                if(key!=book_id):
                    h=Heap(toheap)
                    h.make_minheap()
                    count=count+1
            else:  #对其余数据与小顶堆顶进行比较，若余弦大于小顶堆堆顶元素，则将堆顶置换并重新调整堆
                count=count+1
                if(key!=book_id):
                    cos=self.getcos(vec,value)
                    if (cos>h.heap[0][1]):
                        h.update_heap([key,cos],0)
                        h.modify_heap(0)
        output=h.output_heap()
        return output
'''
if __name__ == '__main__':     
    a=Douban()
    num=a.get_id('无声告白')
    num=a.get_id('无声告白')
    result=a.get_info(num)
    output=a.find_near(num,10)
'''