import pymongo

# MongoDb 配置

MONGO_HOST = '10.192.7.64'
MONGO_PORT = 27017
DB_NAME = 'Articles'

#  mongo数据库的Host, collection设置
Client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
WOS_Articles = Client[DB_NAME]["WOS_Articles"]
WOS_Articles_Ref = Client[DB_NAME]["WOS_Articles_Ref"]
# Financial_Articles = Client[DB_NAME]["Financial_Articles"]
# collection2 = Client[DB_NAME]["Cited_Single"]

