# -*- encoding: utf8 -*-
#Service
PORT_NUM = 7973 #xrange(50051, 50053)
THREAD_POOL_NUM = 200

#Runtime Processing (s)
TIME_OUT = 15
#C_TIME_OUT = 5

#APP Limit
TOPIC_LIMIT = 16 #bytes
TEXT_LIMIT = 128 * 3 #words
SKIP_LIMIT = 100000
SKIP_GATE = 10000

#Mongo Direct
DB_HOST = {
    'alpha': ['10.128.112.181:7379', '10.128.112.181:7380'],
    'prod': ['10.10.40.48:7379', '10.10.40.49:7379', '10.10.40.42:7379', '10.10.40.50:7379']
}
DB_USER = 'search'
DB_PSWD = '4Jf8VL39tS7bImO8'
DB_NAME = 'dbops'

#Search Setting
DEFAULT_DB = 'baas1_a'

