import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import sys
from category_measure import SimilarityCalculator

'''
    The K-means clustering of crime data
'''

# initialize Category Similarity Calculate Class
category_calc = SimilarityCalculator()


def manhattan_dis(p, q, category_index, time_index=-1, weight_cat=0.3, weight_time=0.4):
    """
    Calculate the Manhattan Distance, typically handles attribute Time and Category
    :param p:arraylike object
        contains all the attributes of record p
    :param q:arraylike object
        contains all the attributes of record q
    :param category_index:int
        the index of attribute Category in p and q
    :param time_index:int
        the index of attribute Time in p and q
        Time value should be in [00:00, 24:00]
        if attribute Time is not considered, please keep this value as -1
    :param weight_cat:float
        the weight for the attribute Category, since its distance is range from (0, 38)
    :param weight_time:float
        the weight for the attribute Time, since its distance is range from (0, 12)
    :return:
        the distance value
    """
    category_dis = category_calc.category_distance(p[category_index], q[category_index])
    time_dis = 0
    if time_index != -1:
        time_p = eval(p[time_index].replace(':', '.'))
        time_q = eval(q[time_index].replace(':', '.'))
        time_dis = np.min([abs(time_p - time_q), abs(24 - time_p + time_q)])
    sum_dis = category_dis * weight_cat + time_dis * weight_time
    for i in range(len(p)):
        if i != category_index and i != time_index:
            sum_dis += abs(p[i] - q[i])
    return sum_dis


def initial_medoids(data, k):
    """
    Initialize medoids randomly
    :param data: pandas.DataFrame
        the dataset
    :param k: int
        the number of target clusters
    :return:
        medoids and their index in data set
    """
    m = np.shape(data)[0]
    candidates = list(range(m))
    medoids_index = []

    for i in range(k):
        rand = np.random.randint(0, len(candidates))
        medoids_index.append(candidates[rand])
        del candidates[rand]

    return data.iloc[medoids_index], medoids_index


def k_medoids(data, k, category_index, time_index=-1):
    """
    the k medoids algorithm
    :param data:pandas.DataFrame
        the dataset
    :param k:int
        the number of target clusters
    :param category_index:int
        the index of attribute Category in data column
    :param time_index:int
        the index of attribute Time in data column
    :return:
        medoids: the data set of medoids
        medoids_index: the index of medoids in data
        clustering_set: the class of data records
        sse_new: the SSE value
        iter_num: the total iteration round
    """
    m = np.shape(data)[0]

    medoids, medoids_index = initial_medoids(data, k)  # generate initial medoids

    iter_num = 0    # the number of iteration

    clustering_set = np.zeros((m, 2))   # the set of clustering. Each vector is: (cluster_index, distance_to_medoid)
    sse_old = 0
    sse_new = np.inf

    while abs(sse_new - sse_old) > 0.0001:
        sse_old = sse_new

        # apply records to different medoids
        for i in range(m):
            min_dist = np.inf
            min_index = -1
            for j in range(k):
                dis_to_j = manhattan_dis(data.values[i], medoids.values[j], category_index, time_index)
                if dis_to_j < min_dist:
                    min_dist = dis_to_j
                    min_index = j
            clustering_set[i, 0] = min_index
            clustering_set[i, 1] = min_dist
        sse_new = np.sum(clustering_set[:, 1])
        print('SSE of %d' % iter_num + ' iteration is %f' % sse_new)
        iter_num += 1
        if abs(sse_new - sse_old) <= 0.0001:
            return medoids, medoids_index, clustering_set, sse_new, iter_num

        # update the medoids
        do_changed = False
        do_changed_clustering_set = clustering_set.copy()
        do_changed_medoids_index = medoids_index.copy()

        for i in range(k):
            changed = False
            clustering_set_temp = do_changed_clustering_set.copy()
            medoids_index_temp = do_changed_medoids_index.copy()

            cluster_list = []   # records in the i cluster
            for j in range(len(clustering_set)):
                if clustering_set[j, 0] == i:   # clustering_set[x, 0] records the index in [0, k), not the index of medoid in data
                    cluster_list.append(j)

            min_error = 0
            for x in range(len(cluster_list)):
                if medoids_index_temp[i] != cluster_list[x]:
                    min_error += manhattan_dis(data.values[cluster_list[x]], data.values[medoids_index_temp[i]], category_index, time_index)
            min_index = -1
            for j in range(len(cluster_list)):
                error = 0
                for x in range(len(cluster_list)):
                    if j != x:
                        error += manhattan_dis(data.values[cluster_list[j]], data.values[cluster_list[x]], category_index, time_index)
                if error < min_error:
                    changed = True
                    min_index = cluster_list[j]
                    min_error = error
            if changed:
                medoids_index_temp[i] = min_index
                medoids_temp = data.iloc[medoids_index_temp]
                for w in range(m):
                    min_dist_t = np.inf
                    min_index_t = -1
                    for j in range(k):
                        dis_to_j = manhattan_dis(data.values[w], medoids_temp.values[j], category_index, time_index)
                        if dis_to_j < min_dist_t:
                            min_dist_t = dis_to_j
                            min_index_t = j
                    clustering_set_temp[w, 0] = min_index_t
                    clustering_set_temp[w, 1] = min_dist_t
                sse_temp = np.sum(clustering_set_temp[:, 1])
                if sse_temp < sse_new and sse_temp < sse_old:
                    do_changed_medoids_index[i] = min_index
                    do_changed = True
                    break
        if do_changed:
            medoids_index = do_changed_medoids_index
            medoids = data.iloc[medoids_index]

    return medoids, medoids_index, clustering_set, sse_new, iter_num


def calc_silhouette_coefficient(data, clustering_set, category_index, time_index=-1):
    """
    calculate the Silhouette Coeficient for choosing K
    :param data:pandas.DataFrame
        the dataset
    :param clustering_set:np.narry
        the class of data records
    :param category_index:int
        the index of attribute Category in data
    :param time_index:int
        the index of attribute Time in data
    :return:
        the Sillhouette Coeficient value
    """
    m = np.shape(data)[0]
    sum_sc = 0
    for i in range(m):
        a_sum = 0
        a_count = 0
        b_sum = 0
        b_count = 0
        for j in range(m):
            if i != j:
                dis_ij = manhattan_dis(data.values[i], data.values[j], category_index, time_index)
                if clustering_set[i, 0] == clustering_set[j, 0]:
                    a_sum += dis_ij
                    a_count += 1
                else:
                    b_sum += dis_ij
                    b_count += 1
        a = a_sum / a_count if a_count != 0 else np.inf
        b = b_sum / b_count if b_count != 0 else np.inf
        sum_sc += (b - a) / np.max([a, b])
    return sum_sc / m


def plot(data, x_index, x_name, y_index, y_name, clustering_set, outputFileName):
    """
    generate the plot file of the clustering result
    :param data:pandas.DataFrame
        the dataset
    :param x_index:int
        the index of X-axis attribute in data
    :param x_name:string
        the name of X-axis attribute
    :param y_index:int
        the index of Y-axis attribute in data
    :param y_name:string
        the name of Y-axis attribute
    :param clustering_set:np.narry
        the class of data records
    :param outputFileName:string
        the output filename
    :return: null
    """
    num, dim = np.shape(data)
    mark_samples = ['og', 'ob', 'or', 'oc', 'oy', 'ok', '^g', '^b', '^r', '^c', '^y', '^k', '<g', '<b', '<r', '<c', '<y', '<k']
    for i in range(num):
        plt.plot(float(data[i, x_index].replace(':', '.')), data[i, y_index], mark_samples[int(clustering_set[i, 0])], markersize=5)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.title(outputFileName)
    plt.savefig(outputFileName + '.png')


#############################################################################################
k_value = 5
if len(sys.argv) > 1:
    k_value = eval(sys.argv[1])
    print('Run as k = %d' % k_value)

input_path='Police_Department_Incident_Reports__Historical_2003_to_May_2018-2017-sample-500.csv'
if len(sys.argv) > 2:
    input_path = sys.argv[2]
    print('The input path is: ' % input_path)
raw_data = pd.read_csv(input_path)
data = raw_data[['Category','Time','X','Y']]

medoids, medoids_index, clustering_set, sse, iter_num = k_medoids(data, k_value, 0, 1)
sc_value = calc_silhouette_coefficient(data, clustering_set, 0, 1)


# save results
outputFileName = 'result-k-%d-time-' % k_value + dt.datetime.now().strftime('%H-%M-%S')

# plot
category = np.unique(data['Category'])
for i, e in enumerate(category):
    exec('data[\'Category\'][data[\'Category\']==\'' + e + '\'] = %d' % i)
plot(data.values, 1, 'Time', 0, 'Category', clustering_set, outputFileName)
mark_samples = ['green dot', 'blue dot', 'red dot', 'cyan dot', 'yellow dot', 'black dot', 'green triangle',
                'blue triangle', 'red triangle', 'cyan triangle', 'yellow triangle', 'black triangle', '<g',
                '<b', '<r', '<c', '<y', '<k']

with open(outputFileName+'.txt', 'w') as f:
    f.write('######################################################################\n')
    f.write('Total iteration: %d' % iter_num + ' SSE: %f' % sse + ' S_C: %f' % sc_value)
    f.write('\n\n')
    f.write('######################################################################\n')
    f.write('Medoids Index in Dataset:\n%d' % medoids_index[0])
    for i in range(len(medoids_index)-1):
        f.write(', %d' % medoids_index[i+1])
    f.write('\n\n')
    f.write('######################################################################\n')
    f.write('Records Cluster No:\n%d' % clustering_set[0, 0])
    for i in range(len(clustering_set)-1):
        f.write(', %d' % clustering_set[i+1, 0])
    f.write('\n\n')
    f.write('######################################################################\n')
    f.write('Category Index in Y-Axis:\n')
    for i, e in enumerate(category):
        f.write(e + ' -> %d ' % i + '\n')

with open(outputFileName+'-plot.json', 'w') as f:
    f.write('[')
    for i, e in enumerate(category):
        if i != len(category)-1:
            f.write('["'+e + '",%d],' % i)
        else:
            f.write('["' + e + '",%d]' % i)
    f.write(']')

# output the clustering data in Json
columns = np.array(data.columns).tolist()
columns.append('class')
values = np.array(data.values).T.tolist()
values.append(clustering_set[:, 0])
values = np.array(values).T
values = values.tolist()
data = pd.DataFrame(data=values, columns=columns)
data.to_json(outputFileName + '-data.json',orient='records')