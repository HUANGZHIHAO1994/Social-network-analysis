from sklearn.metrics.pairwise import paired_distances
import numpy as np


def cos(vec1, vec2):
    dot_product = 0.0
    normA = 0.0
    normB = 0.0
    for a, b in zip(vec1, vec2):
        dot_product += a * b
        normA += a ** 2
        normB += b ** 2
    return dot_product / ((normA * normB) ** 0.5)


def cos_sim(vector_a, vector_b):
    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a
    :param vector_b: 向量 b
    :return: sim
    """
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim


result = []
# query = "PATTERN RECOGNITION"
# query = "QUANTITATIVEFINANCE"
query = "MACHINELEARNING"

with open("./output.txt") as f:
    for line in f:
        if line.startswith("v" + query):
            X = line.split()[1:]
            break
        if line.startswith("a" + query):
            X = line.split()[1:]
            break

with open("./output.txt") as f:
    for line in f:
        if line.startswith("v"):
            print(line)
            score = cos(list(map(float, X)), list(map(float, line.split()[1:])))
            # score = pairwise_distances(X, line.split()[1:])
            result.append([score, line[1:].split()[0]])

result.sort()
result = result[::-1]
# 相似度降序排名
result = result[0:20]
# 取相似度前10名
f = open('result.txt', 'w')
for i in range(20):
    f.write(result[i][1] + "\n")
f.close()
