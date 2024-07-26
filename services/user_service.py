from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime
class Users:
        def __init__(self) -> None:
            self.conn = psycopg2.connect(host="localhost",dbname="postgres", user="postgres", password="kaan2002", port=5432)
            self.cur = self.conn.cursor()
            self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INT PRIMARY KEY,
                        username VARCHAR(255),
                        chat_id INT,
                        permission VARCHAR(255)
                        );
    """)
            self.cur.execute("""CREATE TABLE IF NOT EXISTS auditlogs (
                        
                        log VARCHAR(255)

                        );
    """)
            self.conn.commit()
            self.highest_id = self.highest_id()


        def add_log(self,message):
            current_time = datetime.now().time()
            message = f'{message} : at time {current_time}'
            self.cur.execute("INSERT into auditlogs (log) VALUES(%s)", (message,) )
            self.conn.commit()


        def highest_id(self):
            self.cur.execute("""
            SELECT MAX(id) FROM users 
                            """)
            query_result = self.cur.fetchone()
            if query_result == (None,):
                return 0
            return query_result[0]
        
        def get_chat_id_from_username(self,username):
            self.cur.execute("""
            SELECT chat_id FROM users WHERE username=%s
                            """,(username,))
            query_result = self.cur.fetchone()
            if query_result == (None,):
                return 0
            return query_result[0]
             
        def get_username_from_chat_id(self,chat_id):
            self.cur.execute("""
            SELECT username FROM users WHERE chat_id=%s
                            """,(chat_id,))
            query_result = self.cur.fetchone()
            if query_result == (None,):
                return 0
            return query_result[0]
        def get_all_admin_chat_id(self):
            self.cur.execute("""
            SELECT chat_id FROM users WHERE permission='admin'
                            """)
            query_result = self.cur.fetchone()
            if query_result == (None,):
                return 0
            return query_result