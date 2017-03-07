#Service
PORT_NUM = [50051] #xrange(50051, 50053)
THREAD_POOL_NUM = 200

#Runtime Processing (s)
TIME_OUT = 15
CC_TIME_OUT = 1

#Web Scraper
WEB_SCP_HOST = '10.128.112.27'
WEB_SCP_HOST = 'tpe-webscraper-service.tyd.svc.cluster.local'
WEB_SCP_PORT = '1969'
WEB_SCP_PATH = '/v1/webscraper'
WEB_SCP_MODE = 'POST'

#Database Access SDK 
DB_API_HOST = 'localhost'
DB_API_PORT = '9051'
DB_API_VERSION = '1'
DB_OBJ_LIST_LIMIT = 100
#ROOT = process.cwd()

#FILE UPLOAD
FILE_API_HOST = 'tpe-file-upload'
FILE_API_PORT = '31125'
FILE_API_PATH = '/v1/backend/file/upload'

#Code Base Settings
CODEBASE_ROOT = '/root/source_base/app'
CODEBASE_ROOT = 'test'
CODEBASE_TEMP = 'temp'

BLOCK = 'block.py'
