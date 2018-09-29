# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from douban import Douban,Heap
a=Douban()
print('####基于内容的豆瓣图书推荐系统####')
print('本系统可为您推荐您感兴趣的书籍的相关书籍!')
print('#######################################')
judge=1
while(judge!='0'):
    print('请输入您想查询的书籍名称')
    name=input()
    book_id=a.get_id(name)
    if book_id==-1:
        print('抱歉暂时没有您想查找的书籍！ 按“1”继续查询，按“0”结束程序')
        judge=input()
    else:
        print('请输入您想查找的最相关书籍数量')
        n=input()
        results=a.find_near(book_id,int(n))
        print('查询结果为:')
        while(len(results)):
            data=results.pop()
            info=a.get_info(data[0])
            print(info[1]+'   相关度: '+str(data[1]))
            print('作者： '+info[2]+info[3]+'    评分:'+str(info[4]))
            print('简介： '+info[5])
            print('**************************************************************************************')
        print('按“1”继续查询，按“0”结束程序')
        judge=input()
