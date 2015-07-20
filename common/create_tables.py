#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys


class create_sources():
    def orm_create_(id_, database):
        """
        if not exists create db
        """
        if id_ != 1:
            print "revision is too old"
            sys.exit(1)

        try:
            con = psycopg2.connect(database='postgres', user='postgres')
            cur = con.cursor()
            cur.execute("CREATE DATABASE %s;", database)
            cur.commit()

        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()
                print 'Error %s' % e
                sys.exit(1)

        finally:
            if con:
                con.close()

    def create_table(class_id):
        """
        create class table
        """
        stmt = """CREATE TABLE %s (student_name varchar(200), classes_missed integer,
                id integer, PRIMARY KEY(id) );""", class_id
        try:
            con = psycopg2.connect(database='recognise', user='synod')
            cur = con.cursor()
            cur.execute(stmt)

        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()
                print 'Error %s' % e
                sys.exit(1)

        finally:
            if con:
                con.close()
