from fastapi_storages import S3Storage

from app.core.config import settings


class ImageS3Storage(S3Storage):
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_S3_BUCKET_NAME = settings.AWS_S3_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = settings.AWS_S3_ENDPOINT_URL
    AWS_DEFAULT_ACL = settings.AWS_DEFAULT_ACL
    AWS_S3_USE_SSL = settings.AWS_S3_USE_SSL

    def get_path(self, name: str) -> str:
        key = self.get_name(name)
        return f"{self._http_scheme}://{self.AWS_S3_ENDPOINT_URL}/{self.AWS_S3_BUCKET_NAME}/{key}"


img_storage = ImageS3Storage()
