# Keyword search engine
A application of search keywords on the baas, and all connections come from the goBuster through GRPC.

Author:
    Evan

Init:
    ./setup
    
    ATTENTION: If you execute "setup", all of these would be can not to rollback. And almost files will be deleted.

Service start
    ./start

    ATTENTION: It service will take the file of config.py, and you need to reset the host name or others settings before execute it.

Function Test:
    ./test

    ATTENTION: Just can work in localhost, but you can re-wirte the settings of a testClient.py file.
