#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3
import json
from operator import itemgetter

import tornado.web
import tornado.websocket

from settings import DB_PATH, APP_ADDRESS, APP_WEBSOCK_PATH


def dict_factory(cursor, row):
    """
    Function to return sql select result as dictionary.
    """

    return dict(
        zip(
            map(itemgetter(0), cursor.description),
            row
        )
    )

db_connection = sqlite3.connect(DB_PATH)


class MainHandler(tornado.web.RequestHandler):
    """
    Main app handler.
    """

    # noinspection PyMethodOverriding
    def initialize(self, app_port):
        self.app_port = app_port

    def get(self):
        self.render(
            'index.html',
            address=APP_ADDRESS,
            port=self.app_port,
            path=APP_WEBSOCK_PATH
        )


class MessageHandler(tornado.web.RequestHandler):
    """
    Handler that implements HTTP API.
    """

    def get(self):
        """
        Method to get all messages from db.
        """

        db_connection.row_factory = dict_factory
        curs = db_connection.execute(
            """
            SELECT rowid, source, datetime(time, 'unixepoch') as time, text, priority
            FROM message;
            """
        )
        db_connection.row_factory = None
        messages = json.dumps(curs.fetchall())
        self.write(messages)

    def post(self):
        """
        Method to add message into db.

        Example:
            curl -X POST -d 'source=8.8.8.8&text=hello&priority=2' \
            http://127.0.0.1:8888/messages/

            priorities:
                1: 'info',
                2: 'warning',
                3: 'error',
                4: 'critical',
        """

        kw = ['source', 'text', 'priority']
        data = map(self.get_argument, kw)

        db_connection.row_factory = dict_factory
        curs = db_connection.cursor()
        curs.execute(
            "INSERT INTO message (source, text, priority) VALUES (?,?,?);",
            data
        )
        _id = curs.lastrowid
        db_connection.commit()
        curs.execute(
            """
            SELECT rowid, source, datetime(time, 'unixepoch') as time, text, priority
            FROM message WHERE rowid = ?;
            """,
            (_id,)
        )
        db_connection.row_factory = None
        message = curs.fetchone()

        WebSocketHandler.add_message(
            json.dumps(message)
        )

    def delete(self):
        """
        Method to delete message from db.

        Example:
            curl -X DELETE http://127.0.0.1:8888/messages/?id=27
        """

        _id = self.get_argument('id')
        curs = db_connection.execute(
            "SELECT * from message WHERE rowid = ?",
            (_id,)
        )
        msg = curs.fetchone()

        if msg:
            with db_connection as c:
                c.execute(
                    "INSERT INTO message_archive values (?,?,?,?)",
                    msg
                )
                c.execute(
                    "DELETE FROM message WHERE rowid = ?",
                    (_id,)
                )
            WebSocketHandler.delete_message(_id)
        else:
            raise tornado.web.HTTPError(400)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def open(self):
        WebSocketHandler.waiters.add(self)

    def on_close(self):
        WebSocketHandler.waiters.remove(self)

    @classmethod
    def add_message(cls, message):
        for waiter in cls.waiters:
            waiter.write_message(message)

    @classmethod
    def delete_message(cls, _id):
        for waiter in cls.waiters:
            waiter.write_message(_id)
