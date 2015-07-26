import redis


class RedisCache():
    def __init__(self, student_id, class_id):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        student_id = self.student_id
        class_id = self.class_id

    def add_student_class(self, student_id, class_id, r):
        r.hset()
