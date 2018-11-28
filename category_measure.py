import pandas as pd
import numpy as np

'''
    This is the similarity measure for Crime Category(Nominal Attribute).
    The measure is defined as:
        1. initialize a Category Description Tree, separate the Categories under the definition in law.
        2. for p and q in Category Set, if p = q, D(p, q) = 0; if p does not equal q, get their 
        ancestor node p' and q' iteratively until Parent_Node(p') = Parent_Node(q'), note Parent_Node(p') = r.
        3. Define s(p, q) = the number of child leaf nodes of p' + the number of child leaf nodes of q'.
        Define c(r) = MAX{s(x, y)}, where x, y is child nodes of r
        Define the distance metric as: D(p, q) = c(r)
'''


class SimilarityCalculator:

    def __init__(self):
        self.category_tree = {}  # key: node name; value: parent node name
        self.category_leaf_count = {}  # key: node name; value: the number of leaf nodes it contains(including sub
        # leaf nodes)
        self.category_node_layer = {}  # key: node name; value: the layer in the tree
        self.similarity = {}  # key: node name; value: the similarity value

        tree_value = pd.read_csv('./category_tree.csv').values

        parents = np.unique(tree_value[:, 1])
        childs = {}
        for i in range(len(parents)):
            childs[parents[i]] = []
            self.similarity[parents[i]] = 0

        for i in range(tree_value.shape[0]):
            self.category_tree[tree_value[i, 0]] = tree_value[i, 1]
            self.category_leaf_count[tree_value[i, 0]] = tree_value[i, 2]
            self.category_node_layer[tree_value[i, 0]] = tree_value[i, 3]
            if tree_value[i, 0] !=  tree_value[i, 1]:
                childs[tree_value[i, 1]].append(tree_value[i, 0])

        for i in range(parents.shape[0]):
            for j in range(len(childs[parents[i]])):
                for k in range(len(childs[parents[i]])):
                    if j != k:
                        temp = self.category_leaf_count[childs[parents[i]][j]] + self.category_leaf_count[childs[parents[i]][k]]
                        if temp > self.similarity[parents[i]]:
                            self.similarity[parents[i]] = temp

        # min-max normalization, min is 0
        max = np.max(list(self.similarity.values()))
        self.distance = self.similarity.copy()
        for k,v in self.distance.items():
            self.similarity[k] = v / max

    def category_similarity(self, p, q):
        """
            Calculate the similarity between category p and q, and do min-max scaling

            Parameters
            ----------
            p : string
                Crime category element p to calculate similarity with q.
            q : string
                Crime category element q to calculate similarity with p.
            note: There is no error handler, please make sure that p, q is in the category set.
            Returns
            -------
            value : double
                The output value of D(p, q) under min-max scaling
        """
        if p == q:
            return 0
        target_nodes = self.find_target_node(p, q)
        return self.similarity[target_nodes[0]]

    def category_distance(self, p, q):
        """
            Calculate the distance between category p and q.
            Difference from similarty: has not been min-max scaled.

            Parameters
            ----------
            p : string
                Crime category element p to calculate similarity with q.
            q : string
                Crime category element q to calculate similarity with p.
            note: There is no error handler, please make sure that p, q is in the category set.
            Returns
            -------
            value : double
                The output value of D(p, q).
        """
        if p == q:
            return 0
        target_nodes = self.find_target_node(p, q)
        return self.distance[target_nodes[0]]

    def find_target_node(self, p, q):
        """
            Find p' and q' whose parent node is the same.

            Parameters
            ----------
            p : string
                Crime category element p to calculate similarity with q.
            q : string
                Crime category element q to calculate similarity with p.
            Returns
            -------
            value : list
            return p', q', and their parent r
            [r, p', q']
        """
        if self.category_tree[p] == self.category_tree[q]:
            return [self.category_tree[p], p, q]
        elif self.category_node_layer[p] > self.category_node_layer[q]:
            return self.find_target_node(self.category_tree[p], q)
        elif self.category_node_layer[p] < self.category_node_layer[q]:
            return self.find_target_node(p, self.category_tree[q])
        else:
            return self.find_target_node(self.category_tree[p], self.category_tree[q])
