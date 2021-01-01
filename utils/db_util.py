from flask import current_app, g

import sqlite3
from app import app

class DBUtily(object):

    @staticmethod
    def get_db():
        db = getattr(g, "_database", None)
        if db is None:
            db = sqlite3.connect("db/globomantics.db")
        return db

    @app.teardown_appcontext
    def close_connection(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @staticmethod
    def check_if_item_exists(item_id):
        conn = DBUtily.get_db()
        cur = conn.cursor()
        cur.execute("select * from items where id = ?", (item_id,))
        row = cur.fetchone()
        try:
            item = {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "price": row[3],
                "image": row[4]
            }
        except:
            item = {}
        
        return item
    
    @staticmethod
    def get_categories():
        conn = DBUtily.get_db()
        cur = conn.cursor()
        cur.execute("select id, name from categories")
        categories = cur.fetchall()
        return categories
    
    @staticmethod
    def get_subcategory_by_category_id(category_id):
        conn = DBUtily.get_db()
        cur = conn.cursor()
        cur.execute("select id, name from subcategories where category_id = ?", (category_id,))
        subcategories = cur.fetchall()
        return subcategories

    @staticmethod
    def get_subcategories():
        conn = DBUtily.get_db()
        cur = conn.cursor()
        cur.execute("select id, name from subcategories")
        subcategories = cur.fetchall()
        return subcategories
    
    @staticmethod
    def validate_subcategor(id, category_id):
        conn = DBUtily.get_db()
        cur = conn.cursor()
        cur.execute("select count(*) from subcategories where id = ? and category_id = ?", (id, category_id))
        exists = cur.fetchone()[0]
        return exists
    @staticmethod
    def get_comments_by_item_id(item_id):
        conn = DBUtily.get_db()
        cur = conn.cursor()
        cur.execute("select content from comments where item_id = ? order by id desc", (item_id,))
        comments = cur.fetchall()
        return comments
    @staticmethod
    def add_new_comment(content, item_id):
        conn = DBUtily.get_db()
        cur = conn.cursor()
        cur.execute("insert into comments(content, item_id) values(?, ?)", (content, item_id))
        conn.commit()