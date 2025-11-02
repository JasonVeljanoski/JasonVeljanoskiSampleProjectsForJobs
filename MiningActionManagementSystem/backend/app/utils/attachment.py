import os
import uuid


def filename_randomizer(base_name, suffix):
    """return a unique filename"""
    scrambler = str(uuid.uuid4())
    return f"{base_name}_{scrambler}.{suffix}"


def upload_attachments(db, attachment_cls, id, user, files, file_metadatas):
    from app import crud, utils
    from app.schemas.enums import DocumentPaths

    # TODO - add max file size logic (50MB)
    # TODO - black list
    # black_list = [
    #     "",
    #     "exe",
    #     "scr",
    #     "vbs",
    #     "js",
    #     "xml",
    #     "docm",
    #     "xps",
    #     "iso",
    #     "img",
    #     "arj",
    #     "lzh",
    #     "r01",
    #     "r14",
    #     "r18",
    #     "r25",
    #     "tar",
    #     "ace",
    #     "jar",
    #     "rtf",
    #     "pub",
    # ]

    attachments = []
    black_list = []

    # sanity check
    if len(files) != len(file_metadatas):
        raise utils.errors.FileUpload

    # upload file and create db entry
    for ii in range(len(files)):
        file = files[ii]
        file_metadata = file_metadatas[ii]
        fname = file.filename
        ext = fname.split(".")[-1]
        unique_fname = utils.filename_randomizer(fname.split(".")[0], ext)
        path = f"{DocumentPaths.GENERAL.value}/{unique_fname}"
        size = 0
        title = file_metadata.title
        description = file_metadata.description

        if ext in black_list:
            continue

        try:
            with open(path, "wb") as f:
                f.write(file.file.read())
                size = os.path.getsize(path)
        except:
            raise utils.errors.FileUpload

        attachment = crud.general_attachment.create(
            db,
            attachment_cls(
                item_id=id,
                title=title,
                description=description,
                unique_filename=unique_fname,
                filename=fname,
                size=size,
                uploaded_by=user.id,
            ),
        )
        attachments.append(attachment)

    return attachments
