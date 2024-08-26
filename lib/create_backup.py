import semver
from weaviate.backup.backup import BackupCompressionLevel, BackupConfigCreate

import lib.common as common
import weaviate.classes.config as wvc


def create_backup(
    host, api_key, port, backup_id, backend, include, exclude, wait, cpu_for_backup
):

    client = common.connect_to_weaviate(host, api_key, port)

    version = semver.Version.parse(client.get_meta()["version"])
    if include:
        for collection in include.split(","):
            if not client.collections.exists(collection):
                raise Exception(
                    f"Collection '{collection}' does not exist in Weaviate. Cannot include in backup."
                )
    if exclude:
        for collection in exclude.split(","):
            if not client.collections.exists(collection):
                raise Exception(
                    f"Collection '{collection}' does not exist in Weaviate. Cannot exclude from backup."
                )

    result = client.backup.create(
        backup_id=backup_id,
        backend=backend,
        include_collections=include.split(",") if include else None,
        exclude_collections=exclude.split(",") if exclude else None,
        wait_for_completion=wait,
        config=(
            BackupConfigCreate(
                cpu_percentage=cpu_for_backup,
            )
            if version.compare(semver.Version.parse("1.25.0")) > 0
            else None
        ),
    )

    if wait and result and result.status.value != "SUCCESS":
        raise Exception(
            f"Backup '{backup_id}' failed with status '{result.status.value}'"
        )

    print(f"Backup '{backup_id}' created successfully in Weaviate.")

    client.close()
