import os
from collections import defaultdict

import supervisely_lib as sly

sly.Rectangle.from_json()
my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ["modal.state.slyProjectId"])

KEY_TAG_NAME = os.environ["modal.state.keyTagName"]
TAG_NAME = os.environ["modal.state.tagName"]
JSON_PATH_REMOTE = None

PROJECT = None
META: sly.ProjectMeta = None


def read_and_validate_project_meta():
    global META
    meta_json = my_app.api.project.get_meta(PROJECT_ID)
    META = sly.ProjectMeta.from_json(meta_json)
    tag_meta = META.get_tag_meta(TAG_NAME)
    if tag_meta is None:
        raise ValueError("Tag {!r} not found in project {!r}".format(TAG_NAME, PROJECT.name))


def main():
    global PROJECT, JSON_PATH_REMOTE
    api: sly.Api = my_app.api

    PROJECT = my_app.api.project.get_info_by_id(PROJECT_ID)
    if JSON_PATH_REMOTE is None:
        JSON_PATH_REMOTE = "{}_{}".format(PROJECT.id, PROJECT.name)

    read_and_validate_project_meta()

    x = api.project.url()

    result = {
        "project_id": PROJECT.id,
        "project_name": PROJECT.name,
        "project_url": api.project.url(),
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


if __name__ == "__main__":
    sly.main_wrapper("main", main)
