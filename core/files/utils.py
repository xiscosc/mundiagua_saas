import uuid

from django.db.models import Model
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseForbidden, \
    HttpResponseRedirect
from django.urls import reverse_lazy

from core.aws.s3_utils import generate_s3_document_key
from core.files.models import DecoupledFile, FileType, DecoupledImage, DecoupledDocument
from core.files.service import UploadFileService, ImageUploadService, DocumentUploadService
from core.models import User
from intervention.models import Intervention


def intervention_images_to_fs(intervention: Intervention, ifs: ImageUploadService):
    for i in intervention.get_images():
        f = DecoupledImage(uuid.uuid1().__str__(), i.s3_key, i.filename(), i.thumbnail_s3_key, i.user, i.intervention.__str__(), i.date.strftime("%d/%m/%Y %H:%M:%S"))
        ifs.store_file(f)


def intervention_documents_to_fs(intervention: Intervention, ifs: DocumentUploadService):
    for i in intervention.get_documents():
        f = DecoupledDocument(uuid.uuid1().__str__(), i.s3_key, i.filename(), i.user, i.intervention.__str__(), not i.only_officer, i.date.strftime("%d/%m/%Y %H:%M:%S"))
        ifs.store_file(f)


def get_items_in_json_response(m: Model, file_type: str, user: User, download_url_name: str,
                               url_kwargs: dict, meta_url_name: str) -> HttpResponse:
    try:
        fs = _get_fs(file_type)
        files = fs.get_model_items(m)
        if not user.is_officer:
            files = list(filter(lambda x: x.visible_to_all, files))
        return JsonResponse(data=files_to_json(fs, files, download_url_name, url_kwargs, meta_url_name), safe=False)
    except ValueError:
        return HttpResponseBadRequest()


def _get_fs(file_type: str) -> UploadFileService:
    ft = FileType(file_type)
    if ft == FileType.IMAGE:
        return ImageUploadService()
    else:
        return DocumentUploadService()


def files_to_json(fs: UploadFileService, files: list[DecoupledFile], download_url_name: str, url_kwargs: dict,
                  meta_url_name: str) -> list[object]:
    json_fs = []
    for f in files:
        kwargs = url_kwargs.copy()
        kwargs['file_id'] = f.file_id
        json_f = {
            'model': f.model,
            'downloadUrl': reverse_lazy(download_url_name, kwargs=kwargs),
            'thDownloadUrl': fs.get_th_download_url(f),
            'visible': f.visible_to_all,
            'originalFileName': f.original_filename,
            'fileType': f.file_type.value,
            'fileId': f.file_id,
            'userName': f.user.__str__(),
            'userId': f.user.id,
            'createdAt': f.date,
            'metaUrl': reverse_lazy(meta_url_name, kwargs=kwargs),
        }
        json_fs.append(json_f)

    return json_fs


def store_file_metadata_from_post(post_data, m: Model, file_type: str, user: User) -> HttpResponse:
    try:
        fs = _get_fs(file_type)
        file_name = post_data.get("originalFilename", None)
        if not file_name:
            return HttpResponseBadRequest()

        s3_key = generate_s3_document_key(m, file_name)
        file_id = uuid.uuid1().__str__()
        if FileType(file_type) == FileType.IMAGE:
            th_key = "th/" + s3_key
            f = DecoupledImage(file_id, s3_key, file_name, th_key, user, m.__str__())
        else:
            f = DecoupledDocument(file_id, s3_key, file_name, user, m.__str__(), False)

        fs.store_file(f)
        return JsonResponse(data=fs.get_upload_post(f), safe=False)
    except ValueError:
        return HttpResponseBadRequest()


def get_file_metadata(file_id: str, m: Model, file_type: str, user, download_url_name: str,
                      url_kwargs: dict, meta_url_name: str) -> HttpResponse:
    try:
        fs = _get_fs(file_type)
        file = fs.get_item(m, file_id)
        if not file or (not user.is_officer and not file.visible_to_all):
            return HttpResponseNotFound()

        return JsonResponse(data=files_to_json(fs, [file], download_url_name, url_kwargs, meta_url_name)[0],
                            safe=False)
    except ValueError:
        return HttpResponseBadRequest()


def update_file_metadata(file_id: str, m: Model, file_type: str, user, visible: bool) -> HttpResponse:
    try:
        if not user.is_officer:
            return HttpResponseForbidden()

        fs = _get_fs(file_type)
        file = fs.get_item(m, file_id)
        if not file:
            return HttpResponseNotFound()

        file.set_visible_to_all(visible)
        fs.store_file(file)
        return JsonResponse(data={}, safe=False)
    except ValueError:
        return HttpResponseBadRequest()


def get_file_download_url(file_id: str, m: Model, file_type: str, user) -> HttpResponse:
    try:
        fs = _get_fs(file_type)
        file = fs.get_item(m, file_id)
        if not file or (not user.is_officer and not file.visible_to_all):
            return HttpResponseNotFound()

        return HttpResponseRedirect(fs.get_download_url(file))
    except ValueError:
        return HttpResponseBadRequest()


def delete_file_metadata(file_id: str, m: Model, file_type: str, user: User) -> HttpResponse:
    try:
        fs = _get_fs(file_type)
        file = fs.get_item(m, file_id)
        if not file:
            return HttpResponseNotFound()

        if file.user.id != user.id:
            return HttpResponseForbidden()

        fs.delete_file(file)
        return JsonResponse(data={}, safe=False)
    except ValueError:
        return HttpResponseBadRequest()
