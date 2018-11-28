import numpy as np
import pandas as pd
import sys
'''
    Preprocessing function of crime data clustering.
'''


class Preprocesser:
    def __init__(self, data_path='./Police_Department_Incident_Reports__Historical_2003_to_May_2018.csv'):
        self.data_path = data_path

    def split_by_date_column(self, split_index, end_index):
        """
            Split the data file by its Date Column

            Parameters
            ----------
            split_index : int
                The split index(start from 0)
            end_index : int
                The end index, (not included)
                That is, [split_index, end_index)
            Returns
            -------
            no return value
        """
        data = pd.read_csv(self.data_path)

        date_value = data.values[:, 4]
        for i, e in enumerate(date_value):
            date_value[i] = date_value[i][split_index:end_index]

        split_set = np.unique(date_value)
        split_raw_num = {}
        for x in split_set:
            split_raw_num[x] = []

        for i, e in enumerate(date_value):
            split_raw_num[e].append(i)

        for x in split_set:
            data.iloc[split_raw_num[x]].to_csv(self.data_path[:-4]+'-'+x.replace('/', '-')+'.csv', index= False)

    def gen_sample(self, sample_size):
        """
        generate samble of data file by sample_size in the same path as the data file
        :param sample_size:int
            the total number of records in a sample
        :return:
        """
        data = pd.read_csv(self.data_path)
        candidates = list(range(np.shape(data)[0]))
        sample_list = []

        for i in range(sample_size):
            rand = np.random.randint(0, len(candidates))
            sample_list.append(candidates   [rand])
            del candidates[rand]

        data.iloc[sample_list].to_csv(self.data_path[:-4] + '-sample-%d' % sample_size + '.csv', index=False)


#################################################################################################################
if len(sys.argv) < 3:
    print('Please input the command:\n[splitByYear|splitByMonth|Sampling]: to split the file by year or month or just sampling the file\n [dataFilePath]: the path of datafile')

command = sys.argv[1]
data_path = sys.argv[2]

# split the data file by years
if(command == 'splitByYear'):
    processer = Preprocesser(data_path)
    processer.split_by_date_column(6, 10)

# split one year's data into months
if(command == 'splitByMonth'):
    processer = Preprocesser(data_path)
    processer.split_by_date_column(0, 2)

# generate samples
if(command == 'Sampling'):
    if(len(sys.argv) < 4):
        print('Please input the number of samples.')
    sample_num = eval(sys.argv[3])
    processer = Preprocesser(data_path)
    processer.gen_sample(sample_num)
