from __future__ import absolute_import, division, unicode_literals
import os
import sys
import numpy as np
import logging
import itertools
from correlation import *
from allennlp.commands.elmo import ElmoEmbedder
import re
import time
import os
from tqdm import tqdm
from config import WOS_Articles
import time


class Sent_Similar:
    def __init__(self, params, fpath):
        # parameters
        self.params = params
        self.fpath = fpath

    @staticmethod
    def get_similarity_by_name(sim_name):
        NAME_TO_SIM = {
            'avg_cosine': avg_cosine,

            'pearson': pearson,
            'spearman': spearman,
            'kendall': kendall,

            'apsyn': apsyn,
            'apsynp': apsynp
        }
        return NAME_TO_SIM[sim_name]

    def sent_similar(self):
        data, samples, data_init = self.loadFile(self.fpath)
        #         print(data_init)
        #         print(data)
        #         print(samples)
        if self.params['word_vec_name'] != 'elmo':
            word2id, word_vec = self.prepare(self.params, samples)
        if self.params['word_vec_name'] == 'elmo':
            # elmo太慢了，sent1其实就一个样本句
            sent1 = self.sentence_embedding_elmo(data["sentences_pair"][0][:1])
            sent2 = self.sentence_embedding_elmo(data["sentences_pair"][1])
        else:
            sent1 = self.sentence_embedding(self.params, data["sentences_pair"][0][:1])
            sent2 = self.sentence_embedding(self.params, data["sentences_pair"][1])

        path = os.path.join(os.path.dirname(__file__), 'similar_results').replace('\\',
                                                                                  '/')
        if not os.path.exists(path):
            os.mkdir(path)

        #         similarities = ['avg_cosine', 'pearson', 'spearman', 'kendall', 'apsyn', 'apsynp']
        for sim in self.params['sim_list']:
            self.params['similarity_name'] = sim
            print("当前跑到第{}次，共{}次：".format(self.params["count"], self.params["all_count"]), self.params['word_vec_name'],
                  self.params['similarity_name'])
            self.params["count"] += 1
            self.params["similarity"] = self.get_similarity_by_name(sim)
            f = open("./similar_results/{}_{}.txt".format(self.params['word_vec_name'],
                                                          self.params['similarity_name']), "w", encoding='utf8')

            scores = []

            for kk in range(len(sent2)):
                #             print(sent1[kk])
                if len(sent2[kk]) == 1:
                    scores.append(-99999)
                #                 print(sent2[kk])
                #                 if set(sent2[kk][0]) == {0.0}:
                #                     scores.append(-99999)
                else:
                    try:
                        #                         print(self.params["similarity"](sent1[0], sent2[kk]))
                        #                         print(isinstance(self.params["similarity"](sent1[0], sent2[kk]), float))
                        #                         print(type(self.params["similarity"](sent1[0], sent2[kk])))
                        if isinstance(float(self.params["similarity"](sent1[0], sent2[kk])), float):
                            scores.append(float(self.params["similarity"](sent1[0], sent2[kk])))
                        else:
                            scores.append(-88888)
                    except Exception as e:
                        print(e)
                        #                         print(sent2)
                        scores.append(-88888)

            rank = 1

            indexs = np.argsort(scores)

            for index in indexs[::-1]:
                #             f.write(str(rank) + "." + '\t' + data_init[index][0] + '\t' + data_init[index][1] + '\t' + str(scores[index]) + '\n')
                f.write(str(rank) + "." + '\t' + data_init[index][1] + '\t' + str(scores[index]) + '\n')
                rank += 1
            f.close()

    def loadFile(self, fpath):
        data = {}
        samples = []
        data_init = [l.split("\t") for l in re.sub(r'\x0c', '', open(fpath, encoding='utf-8-sig').read()).splitlines()]
        #         for i in data_init:
        #             print(i[1])
        #         print(data_init)
        sent1, sent2 = zip(
            *[l.split("\t") for l in re.sub(r'\x0c', '', open(fpath, encoding='utf-8-sig').read()).splitlines()])

        sent1 = [s.split() for s in sent1]

        sent2 = [s.split() for s in sent2]
        #         print(sent2)
        # sort data by length to minimize padding in batcher
        #         sorted_data = sorted(zip(sent1, sent2),
        #                              key=lambda z: (len(z[0]), len(z[1])))
        #         sent1, sent2 = map(list, zip(*sorted_data))

        data["sentences_pair"] = (sent1, sent2)
        samples += sent1 + sent2

        return data, samples, data_init

    def prepare(self, params, samples):
        word_vec_path = self.get_word_vec_path_by_name(self.params["word_vec_name"])
        self.params["wvec_dim"] = 300

        _, word2id = self.create_dictionary(samples)
        self.params["word_vec"] = self.get_wordvec(word_vec_path, word2id)
        return word2id, self.params["word_vec"]

    def get_word_vec_path_by_name(self, word_vec_name):
        WORD_VEC_MAP = {
            'glove': 'glove.840B.300d.w2vformat.txt',
            'word2vec': 'GoogleNews-vectors-negative300.txt',
            # 'fasttext': 'fasttext-crawl-300d-2M.txt',
        }
        base_path = './data/word_vectors/'
        return base_path + WORD_VEC_MAP[word_vec_name]

    # Create dictionary
    def create_dictionary(self, sentences, threshold=0):
        words = {}
        for s in sentences:
            for word in s:
                words[word] = words.get(word, 0) + 1

        if threshold > 0:
            newwords = {}
            for word in words:
                if words[word] >= threshold:
                    newwords[word] = words[word]
            words = newwords
        words['<s>'] = 1e9 + 4
        words['</s>'] = 1e9 + 3
        words['<p>'] = 1e9 + 2

        sorted_words = sorted(words.items(), key=lambda x: -x[1])  # inverse sort
        id2word = []
        word2id = {}
        for i, (w, _) in enumerate(sorted_words):
            id2word.append(w)
            word2id[w] = i

        return id2word, word2id

    # Get word vectors from vocabulary (glove, word2vec, fasttext ..)
    def get_wordvec(self, path_to_vec, word2id,
                    norm=False):
        """
        Loads words and word vectors from a text file
        :param path_to_vec: path to word vector file in word2vec format
        :param word2id: words to load
        :param norm: normalise word vectors
        :return: dict containing word: word vector
        """
        word_vec = {}

        with open(path_to_vec, 'r', encoding='utf-8', errors='ignore') as f:
            next(f)  # always skip the first line, contains num of words and dim
            for line in f:
                word, vec = line.split(' ', 1)
                if word in word2id:
                    np_vector = np.fromstring(vec, sep=' ')
                    if norm:
                        np_vector = np_vector / np.linalg.norm(np_vector)
                    word_vec[word] = np_vector
        return word_vec

    def sentence_embedding(self, params, sentence):
        '''
        :param params:
        :param batch:
        :return: [[[word1_embedding],[word2_embedding], ...], [[],[], ...]]  list of list (sentence) of list (word)
        '''

        embeddings = []

        for sent in sentence:

            sentvec = []
            if len(sent) >= 10:
                #                 print(sent)
                for word in sent:
                    if word in params["word_vec"]:
                        sentvec.append(params["word_vec"][word])
            #             if not sentvec:
            # 10个单词都不到不能作为结论
            else:
                #                 print(sent)
                #                 sentvec = []
                vec = np.zeros(params["wvec_dim"])
                sentvec.append(vec)
            #                 print(sentvec)
            embeddings.append(sentvec)

        return embeddings

    def sentence_embedding_elmo(self, sentence):
        '''
        :param params:
        :param batch:
        :return: [[[word1_embedding],[word2_embedding], ...], [[],[], ...]]  list of list (sentence) of list (word)
        '''

        embeddings = []

        for sent in sentence:
            print(sent)

            elmo = ElmoEmbedder()
            vec = elmo.embed_sentence(sent)
            sentvec = vec[2]
            embeddings.append(sentvec)

        return embeddings


if __name__ == "__main__":

    # l = ["how are glacier caves formed", "how are glacier caves formed", "how are glacier caves formed", "how are glacier caves formed"]
    # l2 = ["A glacier cave is a cave formed within the ice of a glacier .", "Glacier caves are often called ice caves , but this term is properly used to describe bedrock caves that contain year-round ice.", "In physics , circular motion is a movement of an object along the circumference of a circle or rotation along a circular path.", "A partly submerged glacier cave on Perito Moreno Glacier ."]

    abstract = "Company disclosures greatly aid in the process of financial decision-making; therefore, they are consulted by financial investors and automated traders before exercising ownership in stocks. While humans are usually able to correctly interpret the content, the same is rarely true of computerized decision support systems, which struggle with the complexity and ambiguity of natural language. A possible remedy is represented by deep learning, which overcomes several shortcomings of traditional methods of text mining. For instance, recurrent neural networks, such as long short-term memories, employ hierarchical structures, together with a large number of hidden layers, to automatically extract features from ordered sequences of words and capture highly non-linear relationships such as context-dependent meanings. However, deep learning has only recently started to receive traction, possibly because its performance is largely untested. Hence, this paper studies the use of deep neural networks for financial decision support. We additionally experiment with transfer learning, in which we pre-train the network on a different corpus with a length of 139.1 million words. Our results reveal a higher directional accuracy as compared to traditional machine learning when predicting stock price movements in response to financial disclosures. Our work thereby helps to highlight the business value of deep learning and provides recommendations to practitioners and executives. (C) 2017 Elsevier B.V. All rights reserved."
    abstract2 = "Predicting the final closing price of a stock is a challenging task and even modest improvements in predictive outcome can be very profitable. Many computer-aided techniques based on either machine learning or statistical models have been adopted to estimate price changes in the stock market. One of the major challenges with traditional machine learning models is the feature extraction process. Indeed, extracting relevant features from data and identifying hidden nonlinear relationships without relying on econometric assumptions and human expertise is extremely complex and makes deep learning particularly attractive. In this paper, we propose a deep neural network-based approach to predict if the stock price will increase by 25% for the following year, same quarter or not. We also compare our deep learning method against 'shallow' approaches, random forest and gradient boosted machines. To test the proposed methods, KIS-VALUE database consisting of the Korea Composite Stock Price Index (KOSPI) of companies for the period 2007 to 2015 was considered. All the methods yielded satisfactory performance, namely, deep neural network achieved an AUC of 0.806. 'Shallow' approaches, random forest and gradient boosted machines have been used for comparisons.\t0.8960437338192647"
    start = time.perf_counter()

    # # 整个程序跑的时候改下面数字即可
    # num = "51130000"
    #
    # path = "/home/lemuria/ipcc/pdf2txt/ipcc_sent_tokenize/{}_sent.json".format(num)
    #
    # with open("../conclusion.txt", encoding="utf-8") as f:
    #     conclusion = f.read().split('\n')[:-1]
    #
    # with open(path, encoding='utf-8') as f:
    #     # print(f.read())
    #     l2 = eval(f.read())

    limit = 1
    start = 0
    end = 263698
    results = WOS_Articles.find({"topic_field": {'$in': ["deep learning"]}}, no_cursor_timeout=True)

    with open("sentence.txt", "w", encoding="utf-8") as f:
        for result in tqdm(results):

            if result["abstract"] != "":
                f.write(abstract + '\t' + result["abstract"] + '\n')

    # ************************************************************************************************************
    # 避免改多次名称 把句子生成和相似度计算得分排序放入一个文件
    # ************************************************************************************************************ 

    fpath = './sentence.txt'

    word_vectors = [
        'glove',
        #         'fasttext',    #  这个没试过
        'word2vec',
        'elmo',
    ]

    similarities = [
        'avg_cosine',
        'pearson',
        'spearman',
        'kendall',
        'apsyn',
        'apsynp',
    ]

    #  elmo加入笛卡尔积会重复计算词向量，太慢，因此大改，不用笛卡尔积
    experiments = list(itertools.product(word_vectors, similarities))

    params_senteval = {}
    # params_senteval['name'] = num
    all_count = len(experiments)
    params_senteval['all_count'] = all_count
    params_senteval['count'] = 1
    params_senteval['sim_list'] = similarities

    for idx, wv in enumerate(word_vectors):
        word_vec_name = wv
        #         sim_name = experiment[1]

        #         params_senteval = {}
        params_senteval['word_vec_name'] = word_vec_name
        #         params_experiment = {
        #             'word_vec_name': word_vec_name,
        #             'similarity_name': sim_name
        #         }
        #         params_senteval.update(params_experiment)

        #         params_senteval['similarity'] = get_similarity_by_name(
        #             sim_name)

        #         params_senteval['name'] = num
        ss = Sent_Similar(params_senteval, fpath)
        ss.sent_similar()
    #         count += 1

    end = time.perf_counter()
    print('跑一次匹配的用时：{}'.format(end - start))
