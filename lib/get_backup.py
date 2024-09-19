def get_backup(client, backend, backup_id, restore):

    if restore:
        backup = client.backup.get_restore_status(
            backup_id=backup_id,
            backend=backend,
        )
        print(f"Backup ID: {backup.backup_id}")
        print(f"Backup Path: {backup.path}")
        print(f"Backup Status: {backup.status}")
        if "collections" in backup:
            print(f"Collections: {backup.collections}")
    else:
        if backup_id is not None:
            backup = client.backup.get_create_status(
                backup_id=backup_id, backend=backend
            )
            print(f"Backup ID: {backup.backup_id}")
            print(f"Backup Path: {backup.path}")
            print(f"Backup Status: {backup.status}")
            if "collections" in backup:
                print(f"Collections: {backup.collections}")
        else:
            raise Exception("This functionality is not supported yet.")
            # backups = client.backup.list_backups(backend=backend)
            # for backup in backups:
            #     print(f"Backup ID: {backup.backup_id}")
            #     print(f"Backup Path: {backup.path}")
            #     print(f"Backup Status: {backup.status}")
            #     if "collections" in backup:
            #       print(f"Collections: {backup.collections}")
            #     print("------------------------------")
