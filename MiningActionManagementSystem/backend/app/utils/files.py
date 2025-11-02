import io
import os
import uuid
import shutil
import base64


def filename_randomizer(base_name, suffix):
    """return a unique filename"""
    scrambler = str(uuid.uuid4())
    return f"{base_name}_{scrambler}.{suffix}"

def get_file_ext(path):
    _, file_extension = os.path.splitext(path)
    return file_extension


def create_upload_files(files, file_path, base_name, suffix="jpeg"):
    """
    Write files to specified path and return equivilent array of schemas.Attachment

        files: array of base64 byte strings of images
        file_path: path
        base_name: prefix to filename
        suffix: file extension (e.g. jpeg)

        effect: write files to disk
        return: array of schema.Attachment objects
    """
    from app import schemas

    if not files:
        return []

    attachments = []

    # CREATE PROCESS
    for file in files:

        if file:
            file_name = filename_randomizer(base_name, suffix)
            full_path = f"{file_path}/{file_name}"

            # SAVE FILE TO PATH
            # remove meta of byte string --> data:image/jpeg;base64,/9...
            byte_start_indx = file.find(",") + 1
            b64_str_meta_rem = file[byte_start_indx:]
            data = base64.b64decode(b64_str_meta_rem)
            buf = io.BytesIO(data)
            buf.seek(0)
            with open(full_path, "wb") as fd:
                shutil.copyfileobj(buf, fd)

            # UPDATE SCHEMA
            attachments.append(
                schemas.Attachment(filename=file_name, extension=get_file_ext(full_path))
            )

    return attachments
