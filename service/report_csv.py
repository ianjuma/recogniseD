import csv
import psycopg2
import sys


class csvException(Exception):
    pass


def get_class_list(class_id):
    """
    :param class_id
    :return class_attendees list
    """

    try:
        con = psycopg2.connect(database='recognise', user='synod')
        cur = con.cursor()
        cur.execute("SELECT * FROM TABLE %s;", class_id)

        rows = cur.fetchall()
        return rows

    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()
            print 'Error %s' % e
            sys.exit(1)

    finally:
        if con:
            con.close()


class generateCSVReport():
    def __init__(self, class_id):
        """
        :param class_id
        :return: csv
        """
        self.class_id = class_id

    def to_csv(self):
        file_name = 'exports/' + self.class_id + 'report' + '.csv'
        fd = open(file_name, "wb")
        try:
            writer = csv.writer(fd)
            result = get_class_list(self.class_id)

            writer.writerow(('# ID No', 'Student name', 'Classes Missed', 'Dates Missed'))
            for row in result:
                writer.writerow((row[0], row[1], row[2],'null'))

        except csvException, e:
            raise e
        finally:
            fd.close()
