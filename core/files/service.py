from abc import ABC, abstractmethod
from django.conf import settings
from django.db.models import Model

from core.aws.dynamodb_utils import dynamodb_store_item, dynamodb_get_item, dynamodb_get_items, dynamodb_delete_item
from core.aws.s3_utils import get_s3_download_signed_url, get_s3_upload_signed_post
from core.files.models import DecoupledFile, FileType, DecoupledImage, DecoupledDocument
from core.models import User


class UploadFileService(ABC):
    PARTITION_KEY = 'model'
    SORTING_KEY = 'fileId'

    def __init__(self, file_type: FileType):
        self.users = None
        self.table = settings.AWS_FILES_DYNAMODB
        self.file_type = file_type
        if file_type == FileType.IMAGE:
            self.upload_bucket = settings.S3_PROCESSING_IMAGES
            self.download_bucket = settings.S3_IMAGES
        elif file_type == FileType.DOCUMENT:
            self.upload_bucket = settings.S3_DOCUMENTS
            self.download_bucket = settings.S3_DOCUMENTS
        else:
            raise Exception('Invalid file type')

    @abstractmethod
    def store_file(self, file: DecoupledFile):
        item = {'model': file.model, 's3Key': file.s3_key, 'userId': file.user.id, 'visible': file.visible_to_all,
                'originalFileName': file.original_filename, 'fileId': file.file_id, 'fileType': file.file_type.value,
                'created': file.date}
        if file.th_key:
            item['thS3Key'] = file.th_key

        dynamodb_store_item(self.table, item)

    def get_item(self, m: Model, file_id: str) -> DecoupledFile | None:
        item = dynamodb_get_item(self.table, m.__str__(), file_id, self.PARTITION_KEY, self.SORTING_KEY)
        if item:
            return self._db_to_file(item)

        return None

    @abstractmethod
    def delete_file(self, file: DecoupledFile):
        dynamodb_delete_item(self.table, file.model, file.file_id, self.PARTITION_KEY, self.SORTING_KEY)

    def get_download_url(self, file: DecoupledFile) -> str:
        return get_s3_download_signed_url(file.s3_key, self.download_bucket, 60)

    def get_th_download_url(self, file: DecoupledFile) -> str | None:
        if file.th_key:
            return get_s3_download_signed_url(file.th_key, self.download_bucket, 60)
        else:
            return None

    def get_upload_post(self, file: DecoupledFile) -> object:
        return get_s3_upload_signed_post(file.s3_key, self.upload_bucket)

    def get_model_items(self, m: Model) -> list[DecoupledFile]:
        filter_exp = {'field': 'fileType', 'value': self.file_type.value}
        return list(map(lambda x: self._db_to_file(x),
                        dynamodb_get_items(self.table, m.__str__(), self.PARTITION_KEY, filter_exp)))

    def _db_to_file(self, item: dict) -> DecoupledFile:
        if not self.users:
            users_dict = {}
            for x in User.objects.all():
                users_dict[x.pk] = x
            self.users = users_dict

        th_key = None
        if 'thS3Key' in item:
            th_key = item['thS3Key']

        return DecoupledFile(item['fileId'], item['s3Key'], item['originalFileName'], th_key,
                             self.users[item['userId']], item['model'], item['visible'], FileType(item['fileType']),
                             item['created'])


class ImageUploadService(UploadFileService):
    def __init__(self):
        super().__init__(FileType.IMAGE)

    def store_file(self, file: DecoupledImage):
        if file.file_type != FileType.IMAGE:
            raise TypeError('File must be an image')

        super().store_file(file)

    def delete_file(self, file: DecoupledImage):
        if file.file_type != FileType.IMAGE:
            raise TypeError('File must be an image')

        super().delete_file(file)


class DocumentUploadService(UploadFileService):
    def __init__(self):
        super().__init__(FileType.DOCUMENT)

    def store_file(self, file: DecoupledDocument):
        if file.file_type != FileType.DOCUMENT:
            raise TypeError('File must be a document')

        super().store_file(file)

    def delete_file(self, file: DecoupledDocument):
        if file.file_type != FileType.DOCUMENT:
            raise TypeError('File must be a document')

        super().delete_file(file)
