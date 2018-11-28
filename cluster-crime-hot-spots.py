#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# In[47]:


from sklearn.cluster import KMeans


# In[2]:


data = pd.read_csv('D://Downloads//Police_Department_Incident_Reports__Historical_2003_to_May_2018.csv')


# In[25]:


data.head()


# In[108]:


data['Category'].unique()


# In[10]:


array_category = data['Category'].unique()


# In[11]:


map_category = {}
for i in range(len(array_category)):
    map_category[array_category[i]] = i


# In[12]:


map_category


# In[13]:


array_pddistrict = data['PdDistrict'].unique()
map_pddistrict = {}
for i in range(len(array_pddistrict)):
    map_pddistrict[array_pddistrict[i]] = i


# In[22]:


map_pddistrict


# In[32]:


array_day = data['DayOfWeek'].unique()
map_day = {}
for i in range(len(array_day)):
    map_day[array_day[i]] = i


# In[33]:


map_day


# In[19]:


def getHour(arr):
    return int(arr['Time'][:2])
data['Hour'] = data.apply(getHour, axis = 1)


# In[24]:


def getPdDistrict(arr):
    return int(map_pddistrict[arr['PdDistrict']])
data['pddistrict_numeric'] = data.apply(getPdDistrict, axis = 1)


# In[26]:


def getCategory(arr):
    return int(map_category[arr['Category']])
data['category_numeric'] = data.apply(getCategory, axis = 1)


# In[35]:


def getDay(arr):
    return int(map_day[arr['DayOfWeek']])
data['day_numeric'] = data.apply(getDay, axis = 1)


# In[42]:


def getMonth(arr):
    return int(arr['Date'][:2])
data['month'] = data.apply(getMonth, axis = 1)


# In[43]:


data.iloc[0]


# In[51]:


# 存到本地
processed = data.loc[:,['IncidntNum', 'category_numeric', 'pddistrict_numeric', 'day_numeric', 'month', 'Date', 'Hour', 'X', 'Y']]
processed.to_csv('D://Temp//crime.csv')


# In[52]:


data_2017 = data[data['Date'].str.contains('2017')]


# In[61]:


data_2017.head()


# In[84]:


X = []
for i in range(len(data_2017)):
    row = data_2017.iloc[i]
    if row['category_numeric'] == 1:
        X.append([row['pddistrict_numeric'], row['Hour'], row['day_numeric'], row['month']])

#row['category_numeric'], 


# In[85]:


X = np.array(X)


# In[86]:


X[:10]


# In[101]:


kmeans = KMeans(n_clusters=3, random_state=0).fit(X)


# In[102]:


len(kmeans.labels_)


# In[103]:


np.hstack((X[0], [kmeans.labels_[0]], [data_2017.iloc[0]['X'], data_2017.iloc[0]['Y']]))


# In[104]:


output = []
for i in range(len(X)):
    row = data_2017.iloc[i]
    output.append(np.hstack((X[i], [kmeans.labels_[i]], [row['X'], row['Y']])))


# In[105]:


generated_2017 = pd.DataFrame(output)


# In[110]:


generated_2017.head()


# In[107]:


generated_2017.to_json('D://Temp//crime_robbery_2017.json', orient='records')

