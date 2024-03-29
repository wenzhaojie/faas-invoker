import boto3
import io
import pickle
import redis
import base64
import time
import os



class S3:
    def __init__(
        self,
        AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID", None),
        AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY", None),
        S3_BUCKET_NAME=os.environ.get("S3_BUCKET_NAME", None)
    ):
        # 如果环境变量中没有，则不填写
        if AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY is None:
            self.s3_client = boto3.client(service_name='s3', use_ssl=True)
            self.s3_resource = boto3.Session().resource('s3')
        else:
            self.s3_client = boto3.client(service_name='s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, use_ssl=True)
            self.s3_resource = boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            ).resource('s3')
        self.s3_bucket_name = S3_BUCKET_NAME


    def get_file_io(self, file_key):
        bucket = self.s3_resource.Bucket(self.s3_bucket_name)
        obj = bucket.Object(file_key)
        file_io = io.BytesIO()
        obj.download_fileobj(file_io)
        return file_io

    def put_file_io(self, file_key, file_io):
        bucket = self.s3_resource.Bucket(self.s3_bucket_name)
        obj = bucket.Object(file_key)
        obj.put(Body=file_io.getvalue())

    def get_file(self, file_key, file_path):
        begin = time.time()
        self.s3_client.download_file(self.s3_bucket_name, file_key, file_path)
        t = time.time() - begin
        return t, 0

    def put_file(self, file_key, file_path):
        begin = time.time()
        with open(file_path, "rb") as f:
            self.s3_client.upload_fileobj(f, self.s3_bucket_name, file_key)
        t = time.time() - begin
        return t, 0

    def get_obj(self, obj_key):
        print(f"s3_bucket_name: {self.s3_bucket_name}, obj_key: {obj_key}")
        begin = time.time()
        pickle_byte_obj = self.s3_resource.Object(self.s3_bucket_name, obj_key).get()['Body'].read()
        # pickle_byte_obj = self.s3_resource.Bucket(self.s3_bucket_name).Object(obj_key).get()['Body'].read()
        download_t = time.time() - begin
        begin = time.time()
        object = pickle.loads(pickle_byte_obj)
        pickle_t = time.time() - begin
        return object, download_t, pickle_t

    def put_obj(self, obj_key, obj):
        print(f"s3_bucket_name: {self.s3_bucket_name}, obj_key: {obj_key}")
        begin = time.time()
        pickle_byte_obj = pickle.dumps(obj)
        pickle_t = time.time() - begin
        begin = time.time()
        self.s3_resource.Object(self.s3_bucket_name, obj_key).put(Body=pickle_byte_obj)
        # self.s3_resource.Bucket(self.s3_bucket_name).Object(obj_key).put(Body=pickle_byte_obj)
        t = time.time() - begin
        return t, pickle_t


class Redis:
    def __init__(self, host=os.environ.get("REDIS_HOST", "192.168.122.1"), port=os.environ.get("REDIS_PORT", "6379"),
                 password=os.environ.get("REDIS_PASSWORD", "")):
        self.host = host
        self.port = port
        self.password = password
        self.r = redis.Redis(host=self.host, port=self.port)

    def get_file(self, file_key, file_path):
        with open(file_path, "wb") as f:
            begin = time.time()
            base64_data = self.r.get(file_key)
            t = time.time() - begin
            begin = time.time()
            data = base64.b64decode(base64_data)
            f.write(data)
            decode_t = time.time() - begin
        return t, 0

    def put_file(self, file_key, file_path):
        with open(file_path, "rb") as f:
            begin = time.time()
            data = f.read()
            base64_data = base64.b64encode(data)
            encode_t = time.time() - begin
            begin = time.time()
            self.r.set(file_key, base64_data)
            t = time.time() - begin
        return t, 0

    def get_obj(self, obj_key):
        begin = time.time()
        data = self.r.get(obj_key)
        if data is None:
            return None, 0, 0
        t = time.time() - begin
        begin = time.time()
        obj = pickle.loads(data)
        pickle_t = time.time() - begin
        return obj, t, pickle_t

    def put_obj(self, obj_key, obj):
        begin = time.time()
        data = pickle.dumps(obj)
        pickle_t = time.time() - begin
        begin = time.time()
        self.r.set(obj_key, data)
        t = time.time() - begin
        return t, pickle_t

    def list_keys(self):
        keys = self.r.keys()
        str_keys = [str(key)[2:-1] for key in keys]
        return str_keys

    def incr(self, name, amount=1):
        return self.r.incr(name=name, amount=amount)

    def decr(self, name, amount=1):
        return self.r.decr(name=name, amount=amount)

    def set_key(self, key, value):
        self.r.set(key, value)

    def del_key(self, key):
        self.r.delete(key)

    def get_key(self, key):
        return self.r.get(key)


if __name__ == "__main__":

    # redis = Redis(host="127.0.0.1")
    # redis.put_obj("test", "test")

    s3 = S3()
    s3.put_obj("test", "test")
