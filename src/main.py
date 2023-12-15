import os
from collections import defaultdict

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.v1.app_service import AppService

if sly.is_development():
    load_dotenv("debug.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

my_app: AppService = AppService()

TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()
TASK_ID = sly.env.task_id()
PROJECT_ID = int(os.environ.get("modal.state.slyProjectId"))

KEY_IMAGE_FIELD = os.environ["modal.state.keyImageField"]
TAG_NAME = os.environ["modal.state.tag"]

PROJECT = None
META: sly.ProjectMeta = None


def read_and_validate_project_meta():
    global META
    meta_json = my_app.public_api.project.get_meta(PROJECT_ID)
    META = sly.ProjectMeta.from_json(meta_json)
    if TAG_NAME == "":
        raise ValueError("Reference tag name is not defined")
    if KEY_IMAGE_FIELD == "":
        raise ValueError("Key image field is not defined")


@my_app.callback("create_reference_file")
@sly.timeit
def create_reference_file(api: sly.Api, task_id, context, state, app_logger):
    global PROJECT, JSON_PATH_REMOTE

    PROJECT = api.project.get_info_by_id(PROJECT_ID)
    read_and_validate_project_meta()

    file_remote = os.path.join(
        sly.team_files.RECOMMENDED_EXPORT_PATH,
        f"reference_items/{TASK_ID}/{PROJECT.id}_{PROJECT.name}.json",
    )
    app_logger.info("Remote file path: {!r}".format(file_remote))
    if api.file.exists(TEAM_ID, file_remote):
        raise FileExistsError(
            "File {!r} already exists in Team Files. Make sure you want to replace it. "
            "Please, remove it manually and run the app again.".format(file_remote)
        )

    result = {
        "project_id": PROJECT.id,
        "project_name": PROJECT.name,
        "project_url": api.project.url(PROJECT_ID),
        "reference_tag_name": TAG_NAME,
        "key_image_field": KEY_IMAGE_FIELD,
        "all_keys": [],
        "references": defaultdict(list),
    }

    progress = sly.Progress("Processing", PROJECT.images_count, ext_logger=app_logger)
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
                    key_tag = image_info.meta.get(KEY_IMAGE_FIELD)
                    if key_tag is None:
                        app_logger.warn(
                            "Object has reference tag, but image doesn't have key field. Object is skipped",
                            extra={
                                "figure_id": label.geometry.sly_id,
                                "image_id": image_id,
                                "image_name": image_name,
                                "dataset_name": dataset.name,
                            },
                        )
                        continue

                    rect: sly.Rectangle = label.geometry.to_bbox()
                    reference = {
                        "image_id": image_id,
                        "image_name": image_name,
                        "dataset_name": dataset.name,
                        "image_preview_url": api.image.url(
                            TEAM_ID, WORKSPACE_ID, PROJECT.id, dataset.id, image_id
                        ),
                        "image_url": image_info.path_original,
                        KEY_IMAGE_FIELD: key_tag,
                        "bbox": [rect.top, rect.left, rect.bottom, rect.right],
                        "geometry": label.geometry.to_json(),
                    }
                    result["references"][key_tag].append(reference)
            progress.iters_done_report(len(batch))

    result["all_keys"] = list(result["references"].keys())
    file_local = os.path.join(my_app.data_dir, file_remote.lstrip("/"))
    app_logger.info("Local file path: {!r}".format(file_local))
    sly.fs.ensure_base_path(file_local)
    sly.json.dump_json_file(result, file_local)
    file_info = api.file.upload(TEAM_ID, file_local, file_remote)
    api.task.set_output_file_download(
        task_id,
        file_info.id,
        sly.fs.get_file_name_with_ext(file_remote),
        file_info.storage_path
    )
    app_logger.info("Local file successfully uploaded to team files")

    my_app.stop()


def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "TEAM_ID": TEAM_ID,
            "WORKSPACE_ID": WORKSPACE_ID,
            "PROJECT_ID": PROJECT_ID,
            "modal.state.keyImageField": KEY_IMAGE_FIELD,
            "modal.state.tagName": TAG_NAME,
        },
    )

    # Run application service
    my_app.run(initial_events=[{"command": "create_reference_file"}])


if __name__ == "__main__":
    main()
