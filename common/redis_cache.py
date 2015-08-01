import redis


class RedisException(Exception):
    pass


class RedisCache():
    def __init__(self, student_id, class_id):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.student_id = student_id
        self.class_id = class_id
        self.r = r

    # time complexity 0(1)
    def add_student_missed_class(self, student_id, class_id):
        #count_missed = r.hget(student_id, class_id)
        #count_missed += 1
        """
        try:
            if self.r.hexists(student_id, class_id):
                print 'x'
                self.r.hincrby(student_id, class_id, 1)
            else:
                print 'why'
                self.r.hset(student_id, class_id, '1')
        """
        try:
            print self.r.hkeys(student_id)

        except (redis.exceptions.ConnectionError,
                redis.exceptions.BusyLoadingError):
            print 'connection failed'

        except RedisException:
            print 'broad exception - conn  failed'


obj = RedisCache('633917', 4900)
obj.add_student_missed_class('633917', 4900)
