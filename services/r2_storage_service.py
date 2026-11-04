import logging

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class R2StorageError(Exception):
    """No se pudo completar la operación contra el bucket R2."""


class R2StorageService:
    def __init__(
        self,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
    ):
        self.bucket_name = bucket_name
        self.client = boto3.client(
            service_name="s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
                request_checksum_calculation="WHEN_REQUIRED",
                response_checksum_validation="WHEN_REQUIRED",
            ),
        )

    @staticmethod
    def reflection_key(slug: str) -> str:
        return f"reflections/{slug}.webp"

    @staticmethod
    def event_key(slug: str) -> str:
        return f"events/{slug}.webp"

    def upload_reflection_image(self, slug: str, content: bytes) -> str:
        return self._upload_image(self.reflection_key(slug), content)

    def delete_reflection_image(self, slug: str) -> None:
        self._delete_image(self.reflection_key(slug))

    def upload_event_image(self, slug: str, content: bytes) -> str:
        return self._upload_image(self.event_key(slug), content)

    def delete_event_image(self, slug: str) -> None:
        self._delete_image(self.event_key(slug))

    def _upload_image(self, key: str, content: bytes) -> str:
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType="image/webp",
                CacheControl="public, max-age=31536000, immutable",
            )
        except (BotoCoreError, ClientError) as exc:
            logger.exception("No se pudo subir la imagen %s a R2", key)
            raise R2StorageError("No se pudo subir la imagen a Cloudflare R2") from exc
        return key

    def _delete_image(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
        except (BotoCoreError, ClientError):
            logger.exception("No se pudo eliminar la imagen %s de R2", key)
