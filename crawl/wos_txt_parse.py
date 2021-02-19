import os

from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
from config import WOS_Articles

FIELD_LEN = 2

FIELDS = {
    'PT': 'publication_type', 'AU': 'authors', 'AF': 'authors_full_name', 'TI': 'title', 'SO': 'journal', 'DI': '_id',
    'PY': 'pub_year', 'PD': 'pub_date',
    'AB': 'abstract', 'SN': 'issn', 'UT': 'wos_id',
}

JOINED_FIELDS = {'PT', 'TI', 'SO', 'DI', 'PY', 'PD', 'AB', 'TC', 'SN', 'UT'}

JSON_FIELDS, NUM_FIELDS = {'AU'}, {'PY', 'TC'}


financial_topics = ["financial pricing", "financial risk management", "financial risk measurement", "behavior finance",
                    "corporate finance", "fintech", "financial supervision"]
computer_topics = ["deep learning", "machine learning", "social network analysis"]
topic_dict = {"Finance": financial_topics, "CS": computer_topics}

# topic

# financial pricing, financial risk management, financial risk measurement, behavior finance, corporate finance, fintech, financial supervision
# deep learning, machine learning, social network analysis

# big_topic: Finance, CS

num_id = 1
w_path = os.path.join(os.getcwd(), 'WOS')
for big_topic, topic_list in topic_dict.items():
    for topic in topic_list:
        wos_path = os.path.join(w_path, topic)
        filelist = os.listdir(wos_path)

        try:
            filelist.remove('.ipynb_checkpoints')
        except:
            pass
        for file in tqdm(filelist):
            with open(os.path.join(wos_path, file), encoding='utf8', errors='ignore') as f:
                # l.append(f.read().split("\n\n"))
                articles = f.read().replace('\ufeffFN Clarivate Analytics Web of Science\nVR 1.0\n', '').replace(
                    '\n   ', '￥￥￥').split("\n\n")[
                           :-1]
                # print(articles)
                # print(len(articles))
                for article in articles:
                    article_dict = dict({
                        'publication_type': '', 'authors': '', 'authors_full_name': '', 'title': '', 'journal': '',
                        'pub_year': '', 'pub_date': '',
                        'abstract': '', 'issn': '', 'wos_id': '', 'num_id': num_id})
                    article_dict["big_topic"] = big_topic
                    article_dict["topic_field"] = [topic]
                    for field in article.split("\n")[:-1]:

                        if field[:FIELD_LEN] in FIELDS:
                            if field[:FIELD_LEN] in ['AU', 'AF']:
                                field = field.replace('￥￥￥', ';')
                            else:
                                field = field.replace('￥￥￥', ' ')
                            article_dict[FIELDS[field[:FIELD_LEN]]] = field[FIELD_LEN + 1:].strip()

                    # 判断doi 不为空才插入数据库(早一点的文章abstract都没有的)
#                     if article_dict.get('_id') and article_dict.get('authors') and article_dict.get(
#                             'title') and article_dict.get('abstract'):
                    if article_dict.get('_id'):
                        try:
                            WOS_Articles.insert_one(article_dict)
                            num_id += 1
                        except DuplicateKeyError as e:
                            result = WOS_Articles.find_one({'_id': article_dict.get('_id')})
                            # print('#' * 30)
                            # print(type(result))
                            # print(result)
                            # print(result["topic_field"])
                            update_list = result["topic_field"]
                            if topic not in result["topic_field"]:
                                update_list.append(topic)
                                WOS_Articles.update_one({'_id': article_dict.get('_id')},
                                                        {'$set': {"topic_field": update_list}})


