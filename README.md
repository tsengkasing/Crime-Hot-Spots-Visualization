# Crime Hot Spots Visualization

![](https://img.shields.io/badge/Numpy-1.15.x-brightgreen.svg?style=flat-square) ![](https://img.shields.io/badge/pandas-0.23.4-brightgreen.svg?style=flat-square) ![](https://img.shields.io/badge/scikit--learn-0.20.0-brightgreen.svg?style=flat-square)



## Brief Introduction

Using **Clustering** algorithm to dig out the similarity between crime events.

In this demo, we will apply **KMeans** algorithm to cluster the crime data and find out some **similarity** between **robbery** crime events.



## Get Started

- Open Terminal/Cmd/Bash

- Clone this Repo

- Switch to the directory of **build**

- Type `python -m http.server 1234` (MAKE SURE your are using Python **3.x**)

- Open your Browser and visit `http://localhost:1234/`



```bash
$ git clone https://github.com/tsengkasing/Crime-Hot-Spots-Visualization.git
$ cd build
$ python -m http.server 1234
```



Gif of step by step ↓

![crimehotspot-visual-step](https://user-images.githubusercontent.com/10103993/49131409-034b6100-f313-11e8-9db0-46c58db2e487.gif)



## Tiny Conclusion

After several attempts, we cluster the data into 3 cluster.

- **Cluster 1** only appear in **night**(17:00 ~ 23:00)

- **Cluster 2** only appear **before dawn** (0:00 ~ 7:00)

- **Cluster 3** only appear in **day**(8:00 ~ 16:00)



All of them will happen in City Center.

However, **Cluster 1** and **Cluster 2** will happen more in **suburb** .




## Implementation Method Introduction

[P.S.] The following processing code is placed in `cluster-crime-hot-spots.py`.



In the beginning, we download and import the data from **DataSF**(San Francisco's data).

Here is the link [https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-Historical-2003/tmnf-yvry](https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-Historical-2003/tmnf-yvry)

```python
data = pd.read_csv('/path/to/Police_Department_Incident_Reports__Historical_2003_to_May_2018.csv')
```



Next we input the following code ``data['Category'].unique()``.

We can see that there are 39 kinds of crime **category**.

```python
['NON-CRIMINAL', 'ROBBERY', 'ASSAULT', 'SECONDARY CODES',
       'VANDALISM', 'BURGLARY', 'LARCENY/THEFT', 'DRUG/NARCOTIC',
       'WARRANTS', 'VEHICLE THEFT', 'OTHER OFFENSES', 'WEAPON LAWS',
       'ARSON', 'MISSING PERSON', 'DRIVING UNDER THE INFLUENCE',
       'SUSPICIOUS OCC', 'RECOVERED VEHICLE', 'DRUNKENNESS', 'TRESPASS',
       'FRAUD', 'DISORDERLY CONDUCT', 'SEX OFFENSES, FORCIBLE',
       'FORGERY/COUNTERFEITING', 'KIDNAPPING', 'EMBEZZLEMENT',
       'STOLEN PROPERTY', 'LIQUOR LAWS', 'FAMILY OFFENSES', 'LOITERING',
       'BAD CHECKS', 'TREA', 'GAMBLING', 'RUNAWAY', 'BRIBERY',
       'PROSTITUTION', 'PORNOGRAPHY/OBSCENE MAT',
       'SEX OFFENSES, NON FORCIBLE', 'SUICIDE', 'EXTORTION']
```



Due to the large dataset, we will only focus on the events data of **Robbery** in **2017** in this demo.

Before we apply the **KMeans** algorithm, we need to transform the **nominal** attribute to **numeric** attribute.

We mainly focus on 4 attributes `PdDistrict`, `DayOfWeek`, `Hour`, `Month` .

- Build a dictionary of `PdDistrict`

    ```python
    array_pddistrict = data['PdDistrict'].unique()
    map_pddistrict = {}
    for i in range(len(array_pddistrict)):
        map_pddistrict[array_pddistrict[i]] = i
    ```

- Build a dictionary of `DayOfWeek`

    ```python
    array_day = data['DayOfWeek'].unique()
    map_day = {}
    for i in range(len(array_day)):
        map_day[array_day[i]] = i
    ```

- Add New Column

  ```python
  # PdDistrict
  def getPdDistrict(arr):
      return int(map_pddistrict[arr['PdDistrict']])
  data['pddistrict_numeric'] = data.apply(getPdDistrict, axis = 1)
  
  # DayOfWeek
  def getDay(arr):
      return int(map_day[arr['DayOfWeek']])
  data['day_numeric'] = data.apply(getDay, axis = 1)
  
  # Hour
  def getHour(arr):
      return int(arr['Time'][:2])
  data['Hour'] = data.apply(getHour, axis = 1)
  
  # Month
  def getMonth(arr):
      return int(arr['Date'][:2])
  data['month'] = data.apply(getMonth, axis = 1)
  ```

- Select Data of **2017**

    ```python
    data_2017 = data[data['Date'].str.contains('2017')]
    ```

- Build an "X" Matrix with the Data of **Robbery**

    ```python
    X = []
    for i in range(len(data_2017)):
        row = data_2017.iloc[i]
        if row['Category'] == 'ROBBERY':
            X.append([row['pddistrict_numeric'], row['Hour'], row['day_numeric'], row['month']])
    
    X = np.array(X)
    ```

- Apply **KMeans** Algorithm

    ```python
    kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
    ```

- **Clusters** labels

    ```python
    kmeans.labels_
    ```

- Build a new Matrix contains **latitude**("X") and **longitude**("Y")

    ```python
    output = []
    for i in range(len(X)):
        row = data_2017.iloc[i]
        output.append(np.hstack((X[i], [kmeans.labels_[i]], [row['X'], row['Y']])))
    ```

- Save as **json** to local

    ```python
    generated_2017 = pd.DataFrame(output)
    generated_2017.to_json('/path/to/crime_robbery_2017.json', orient='records')
    ```

- Using Google Maps API to visualize the data according `Label` and `Hour` .

    Please refer to the Google Maps Platform Documents

    [https://developers.google.com/maps/documentation/javascript/examples/circle-simple](https://developers.google.com/maps/documentation/javascript/examples/circle-simple)
