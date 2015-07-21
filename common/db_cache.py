#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys


class DBCacheException(Exception):
    """
    basic db cache exception
    """
    pass


class db_cache():
    def __init__():
        pass

    def populate_cache(last_populate):
        """
        populate postgres cache;
        students database table
        """
        pass

    def orm_create_(id_):
        """
        if not exists create tables, db
        """
        pass


def mark_student_absent(student_id, class_id):
    """
    add student field to class missed rel;
    tables for classes
    get student class missed count by ID and add one
    """
    try:
        con = psycopg2.connect(database='recognise', user='synod')
        cur = con.cursor()
        stmt = "UPDATE {0} SET classes_missed = {1} WHERE id = {3};".format(class_id, 1, student_id)

        cur.execute(stmt)

    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()
            print 'Error %s' % e
            sys.exit(1)

    finally:
        if con:
            con.close()
