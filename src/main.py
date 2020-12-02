import os
from collections import defaultdict

import supervisely_lib as sly

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ["modal.state.slyProjectId"])

KEY_TAG_NAME = os.environ["modal.state.keyTagName"]
TAG_NAME = os.environ["modal.state.tagName"]

PROJECT = None
META: sly.ProjectMeta = None


def read_and_validate_project_meta():
    global META
    meta_json = my_app.public_api.project.get_meta(PROJECT_ID)
    META = sly.ProjectMeta.from_json(meta_json)

    if TAG_NAME == "":
        raise ValueError("Reference tag name is not defined")

    if KEY_TAG_NAME == "":
        raise ValueError("Key tag name is not defined")

    for name in [TAG_NAME, KEY_TAG_NAME]:
        tag_meta = META.get_tag_meta(name)
        if tag_meta is None:
            raise ValueError("Tag {!r} not found in project {!r}".format(name, PROJECT.name))


def main():
    global PROJECT, JSON_PATH_REMOTE
    api: sly.Api = my_app.public_api

    PROJECT = api.project.get_info_by_id(PROJECT_ID)
    read_and_validate_project_meta()

    file_remote = "/reference_items/{}_{}.json".format(PROJECT.id, PROJECT.name)
    my_app.logger.info("Remote file path: {!r}".format(file_remote))
    if api.file.exists(TEAM_ID, file_remote):
        raise FileExistsError("File {!r} already exists in Team Files. Make sure you want to replace it. "
                              "Please, remove it manually and run the app again."
                              .format(file_remote))

    result = {
        "project_id": PROJECT.id,
        "project_name": PROJECT.name,
        "project_url": api.project.url(PROJECT_ID),
        "reference_tag_name": TAG_NAME,
        "key_tag_name": KEY_TAG_NAME,
        "all_keys": [],
        "references": defaultdict(list)
    }

    progress = sly.Progress("Processing", PROJECT.images_count, ext_logger=my_app.logger)
    for dataset in api.dataset.get_list(PROJECT.id):
        ds_images = api.image.get_list(dataset.id)
        for batch in sly.batched(ds_images):
            image_ids = [image_info.id for image_info in batch]
            image_names = [image_info.name for image_info in batch]

            ann_infos = api.annotation.download_batch(dataset.id, image_ids)
            anns = [sly.Annotation.from_json(ann_info.annotation, META) for ann_info in ann_infos]

            for image_info, image_id, image_name, ann in zip(batch, image_ids, image_names, anns):
                for label in ann.labels:
                    tag = label.tags.get(TAG_NAME)
                    if tag is None:
                        continue

                    key_tag = label.tags.get(KEY_TAG_NAME)
                    if key_tag is None:
                        my_app.logger.warn("Object has reference tag, but doesn't have key tag. Object is skipped",
                                           extra={"figure_id": label.geometry.sly_id, "image_id": image_id,
                                                  "image_name": image_name, "dataset_name": dataset.name})
                        continue

                    rect: sly.Rectangle = label.geometry.to_bbox()
                    reference = {
                        "image_id": image_id,
                        "image_name": image_name,
                        "dataset_name": dataset.name,
                        "image_preview_url": api.image.url(TEAM_ID, WORKSPACE_ID, PROJECT.id, dataset.id, image_id),
                        "image_url": image_info.full_storage_url,
                        KEY_TAG_NAME: key_tag.value,
                        "bbox": [rect.top, rect.left, rect.bottom, rect.right]
                    }
                    result["references"][key_tag.value].append(reference)
            progress.iters_done_report(len(batch))

    result["all_keys"] = list(result["references"].keys())
    file_local = os.path.join(my_app.data_dir, file_remote.lstrip("/"))
    my_app.logger.info("Local file path: {!r}".format(file_local))
    sly.fs.ensure_base_path(file_local)
    sly.json.dump_json_file(result, file_local)
    api.file.upload(TEAM_ID, file_local, file_remote)
    my_app.logger.info("Local file successfully uploaded to team files")


if __name__ == "__main__":
    main()
    #sly.main_wrapper("main", main)
