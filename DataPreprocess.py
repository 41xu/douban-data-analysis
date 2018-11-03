import pandas as pd
import numpy as np
import os
import re

curdir=os.getcwd()
totaldirs=os.listdir(curdir)
print(totaldirs)

totalcsv=[]
for dir in totaldirs:
    pattern=re.compile('[\d]+\.csv')
    temp=re.findall(pattern,dir)
    if temp!=[]:
        totalcsv.append("".join(temp))
print(totalcsv)
temp=[]
for csv in totalcsv:
    # print(csv)
    temp.append(pd.read_csv(csv))
data=pd.concat(temp)
data.to_csv("data.csv")
print(len(data))