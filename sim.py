#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
usage:
    sim.py run [<port>]
    sim.py init_db

arguments:
    run         run app
    init_db     create database and all needed tables
    <port>      app port number
"""


from docopt import docopt
import tornado.web
import tornado.ioloop

from base import db_connection, MainHandler, MessageHandler, WebSocketHandler
from settings import APP_PORT, APP_WEBSOCK_PATH


if __name__ == '__main__':
    args = docopt(__doc__)

    if args['run']:
        if args['<port>']:
            APP_PORT = args['<port>']

        application = tornado.web.Application([
            (r"/", MainHandler, {'app_port': APP_PORT}),
            (r"/messages/", MessageHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': './static'}),
            (r"/%s/" % APP_WEBSOCK_PATH, WebSocketHandler)
        ])
        application.listen(APP_PORT)
        tornado.ioloop.IOLoop.instance().start()

    elif args['init_db']:
        with db_connection as c:
            c.execute('''
                CREATE TABLE IF NOT EXISTS message
                    (
                        source text NOT NULL,
                        time int DEFAULT (strftime('%s', 'now', 'localtime')),
                        text text NOT NULL,
                        priority int NOT NULL
                    );
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS message_archive
                    (
                        source text NOT NULL,
                        time int NOT NULL,
                        text text NOT NULL,
                        priority int NOT NULL
                    );
            ''')
