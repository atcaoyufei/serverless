import pymongo


class Mongo:

    def __init__(self, dsn, db_name, col_name):
        self.client = pymongo.MongoClient(dsn)
        self.db = self.client.get_database(db_name)
        self.col = self.db.get_collection(col_name)

    def close(self):
        self.client.close()

    def save(self, data: dict):
        _id = data['ip']
        if not data.get('_id'):
            data['_id'] = _id

        if self.col.find_one(_id):
            return self.update({'_id': _id}, data)
        return self.col.insert_one(data).inserted_id

    def update(self, data, condition=None):
        _id = data.get('_id')
        if _id:
            condition = {'_id': _id}
            del data['_id']

        data = {'$set': data}
        return self.col.update_one(condition, data).modified_count

    def get_empty_country_proxy(self) -> list:
        return list(self.col.find({'country': ''}, {'_id': 1}).limit(100))

    def __getattr__(self, item):
        def call_back(*args, **kwargs):
            func = getattr(self.col, item)
            return func(*args, **kwargs)

        return call_back
