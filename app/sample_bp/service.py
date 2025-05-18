from app.extentions import mongo

class SampleService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def sample(self):
        data = mongo.db.collection_name.find_one({"key": "value"})
        if data:
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "message": "No data found"}