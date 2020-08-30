"""

"""
import asyncio
import aiobotocore
import time

from s3clr import helper

logger = helper.get_logger("s3clr")


class S3Cleanup(object):
    def __init__(self, *, bucket: str, prefixes: list, expiry: int = 30):
        self._bucket = bucket
        self._prefixes = prefixes
        self._expiry = expiry
        self._session = aiobotocore.get_session()
        self._queue = asyncio.Queue()
        self._curr_epoch_time = time.time()

    @property
    def queue(self):
        return self._queue

    def _is_expired(self, last_modified_time) -> bool:
        expired_epoch_time = self._expiry * 86400
        expiry_date = self._curr_epoch_time - expired_epoch_time
        if last_modified_time < expiry_date:
            return True
        return False

    @staticmethod
    def _load_aws_secrets():
        """
        Loads all the secrets required to connect to AWS from environment variables
        """
        from os import environ
        from sys import exit
        try:
            region_name = environ.get("AWS_DEFAULT_REGION", "us-west-2")
            aws_access_key_id = environ["AWS_ACCESS_KEY_ID"]
            aws_secret_access_key = environ["AWS_SECRET_ACCESS_KEY"]
            aws_session_token = environ.get("AWS_SESSION_TOKEN", "")

            _secrets = {
                'region_name': region_name,
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key,
                **({'aws_session_token': aws_session_token} if aws_session_token != "" else {})
            }
            return _secrets
        except KeyError as ke:
            logger.error("Please set the environment variables", ke)
            exit(1)

    def _create_client(self):
        return self._session.create_client('s3', **(S3Cleanup._load_aws_secrets()))

    async def s3_list(self):
        async with self._create_client() as client:
            paginator = client.get_paginator('list_objects_v2')
            for prefix in self._prefixes:
                kwargs = {"Bucket": self._bucket, "Prefix": prefix}
                async for result in paginator.paginate(**kwargs):
                    for c in result.get('Contents', []):
                        if self._is_expired(c.get('LastModified').timestamp()):
                            logger.info(f"s3_list - {c.get('Key')}")
                            await self._queue.put({
                                "Key": c.get('Key'),
                                "Size": c.get('Size'),
                                "LastModified": c.get('LastModified')
                            })

    async def s3_delete(self):
        while True:
            async with self._create_client() as client:
                c = await self._queue.get()
                self._queue.task_done()
                resp = await client.delete_object(Bucket=self._bucket, Key=c.get('Key'))
                http_status = resp.get('ResponseMetadata').get('HTTPStatusCode')
                version_id = resp.get('VersionId')
                logger.info(f"s3_delete - {c.get('Key')} - {http_status} - {version_id}")


async def main():
    s3clr = S3Cleanup(bucket="test-delete-something", prefixes=["kubernetes/"], expiry=1)

    # TODO: prepare the producers and consumers based on workload
    producers = [asyncio.create_task(s3clr.s3_list())
                 for _ in range(5)]
    consumers = [asyncio.create_task(s3clr.s3_delete())
                 for _ in range(100)]

    # wait for the producers to finish
    await asyncio.gather(*producers)

    # wait for the remaining tasks to be processed
    await s3clr.queue.join()

    # cancel the consumers, which are now idle
    for c in consumers:
        c.cancel()


asyncio.run(main())
