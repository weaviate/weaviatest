def cancel_backup(client, backend, backup_id):

    result = client.backup.cancel_backup(
        backup_id=backup_id,
        backend=backend,
    )

    if result:
        print(f"Backup '{backup_id}' cancelled successfully.")
    else:
        print(f"Backup '{backup_id}' could not be cancelled. Or it wasn't found.")
