import lib.common as common
import weaviate.classes.config as wvc


def restore_backup(host, api_key, port, backup_id, backend, include, exclude, wait):

    client = common.connect_to_weaviate(host, api_key, port)

    result = client.backup.restore(
        backup_id=backup_id,
        backend=backend,
        include_collections=include.split(",") if include else None,
        exclude_collections=exclude.split(",") if exclude else None,
        wait_for_completion=wait,
    )

    if wait and result and result.status.value != "SUCCESS":
        client.close()
        raise Exception(
            f"Backup '{backup_id}' failed with status '{result.status.value}'"
        )

    print(f"Backup '{backup_id}' restored successfully in Weaviate.")

    client.close()
