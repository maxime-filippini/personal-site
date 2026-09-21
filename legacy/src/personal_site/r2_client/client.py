import contextlib
import datetime
import fnmatch
import pathlib
from tempfile import TemporaryDirectory

import boto3
import botocore
import botocore.response
import polars as pl
import pydantic
from botocore.config import Config


class ListBucketsResponse(pydantic.BaseModel):
    buckets: list[Bucket] = pydantic.Field(alias="Buckets")


class ListObjectsResponse(pydantic.BaseModel):
    contents: list[Object] = pydantic.Field(alias="Contents", default_factory=list)


class Object(pydantic.BaseModel):
    bucket: str = pydantic.Field(alias="Bucket")
    key: str = pydantic.Field(alias="Key")


class ReadObject(pydantic.BaseModel):
    object_: Object
    body: str


class Bucket(pydantic.BaseModel):
    name: str = pydantic.Field(alias="Name")
    creation_date: datetime.datetime = pydantic.Field(alias="CreationDate")


class Client:
    _file_snapshots: list[Object] | None = None

    def __init__(self, url: str, access_key_id: str, secret_access_key: str) -> None:
        self.url = url
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

        self._client = boto3.client(
            "s3",
            endpoint_url=self.url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name="auto",
            config=Config(signature_version="s3v4"),
        )

        self.file_snapshots = None

    @property
    def storage_options(self):
        return {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "region": "auto",
            "aws_endpoint": self.url,
        }

    def list_buckets(self):
        resp = self._client.list_buckets()
        return ListBucketsResponse.model_validate(resp)

    def list_objects(self, bucket_name: str):
        resp = self._client.list_objects_v2(Bucket=bucket_name)

        for obj in resp.get("Contents", []):
            obj["Bucket"] = bucket_name

        return ListObjectsResponse.model_validate(resp).contents

    def read_object(self, object_: Object) -> ReadObject:
        resp = self._client.get_object(Bucket=object_.bucket, Key=object_.key)

        try:
            body: botocore.response.StreamingBody = resp["Body"]
        except KeyError:
            raise

        contents = body.read()
        return ReadObject(object_=object_, body=contents)

    def delete_object(self, bucket_name: str, object_name: str):
        self._client.delete_object(Bucket=bucket_name, Key=object_name)

    def delete_by_pattern(self, bucket_name: str, pattern: str):
        to_delete = [
            file
            for file in self.list_objects(bucket_name)
            if fnmatch.fnmatch(file.key, pattern)
        ]

        for file in to_delete:
            self.delete_object(bucket_name=bucket_name, object_name=file.key)

    def write_df(self, df: pl.DataFrame, bucket_name: str, file_name: str):
        with TemporaryDirectory() as tmp_dir:
            p = pathlib.Path(tmp_dir)
            df.write_parquet(p / file_name)
            self._client.upload_file(str(p / file_name), bucket_name, file_name)

    def object_exists(self, bucket_name: str, object_name: str):
        files = (
            self._file_snapshots
            if self._file_snapshots is not None
            else self.list_objects(bucket_name)
        )
        return (
            next((file for file in files if file.key == object_name), None) is not None
        )

    def get_object(self, bucket_name: str, object_name: str):
        obj = self._client.head_object(Bucket=bucket_name, Key=object_name)
        return Object.model_validate({"Bucket": bucket_name, "Key": object_name, **obj})

    @contextlib.contextmanager
    def file_snapshot(self, bucket_name: str):
        self._file_snapshots = self.list_objects(bucket_name)
        yield self
        self._file_snapshots = None
