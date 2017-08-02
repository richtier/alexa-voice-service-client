from http.server import HTTPServer
import os

import conf, handlers


def main():
    server_address = (conf.ADDRESS, conf.PORT)
    httpd = HTTPServer(server_address, handlers.AmazonAlexaServiceLoginHandler)
    print('running server on http://{}:{}'.format(*server_address))
    httpd.serve_forever()
 
 
if __name__ == '__main__':
    main()
