from enum import Enum

from core.models import User
from datetime import datetime


class FileType(Enum):
    IMAGE = 'image'
    DOCUMENT = 'document'


class DecoupledFile:
    def __init__(self, file_id: str, s3_key: str, original_filename: str, th_key: str | None, user: User, model: str,
                 visible_to_all: bool, file_type: FileType, date: str | None):
        self.file_id = file_id
        self.s3_key = s3_key
        self.original_filename = original_filename
        self.th_key = th_key
        self.user = user
        self.model = model
        self.visible_to_all = visible_to_all
        self.file_type = file_type
        if date:
            self.date = date
        else:
            self.date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class DecoupledImage(DecoupledFile):
    def __init__(self, file_id: str, s3_key: str, original_filename: str, th_key: str, user: User, model: str,
                 date: str | None = None):
        super().__init__(file_id, s3_key, original_filename, th_key, user, model, True, FileType.IMAGE, date)


class DecoupledDocument(DecoupledFile):
    def __init__(self, file_id: str, s3_key: str, original_filename: str, user: User, model: str, visible_to_all: bool,
                 date: str | None = None):
        super().__init__(file_id, s3_key, original_filename, None, user, model, visible_to_all, FileType.DOCUMENT, date)
