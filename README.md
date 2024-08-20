# Weaviatest CLI

CLI tool to perform different Weaviate operations seamlessly. The Weaviatest CLI allows you to create, delete, update, restore, and query various entities in Weaviate.

## Usage

The Weaviatest CLI provides the following actions:

### Create

- Create a class: `weaviatest.py create class --class_name <class_name> --multitenant --vector_index <vector_index> --replication_factor <replication_factor>`
- Create data: `weaviatest.py create data --class_name <class_name> --number_objects <number_objects> --consistency_level <consistency_level> --randomize`
- Create tenants: `weaviatest.py create tenants --class_name <class_name> --number_tenants <number_tenants>`
- Create backup: `weaviatest.py create backup --backup_id <backup_id>`

### Update

- Update class: `weaviatest.py update class --class_name <class_name> --new_class_name <new_class_name>`
- Update tenants: `weaviatest.py update tenants --class_name <class_name> --number_tenants <number_tenants> --state <state>`
- Update data: `weaviatest.py update data --class_name <class_name> --number_objects <number_objects> --consistency_level <consistency_level>`

### Delete

- Delete class: `weaviatest.py delete class --class_name <class_name>`
- Delete data: `weaviatest.py delete data --class_name <class_name>`
- Delete tenants: `weaviatest.py delete tenants --class_name <class_name> --number_tenants <number_tenants>`

### Restore

- Restore backup: `weaviatest.py restore backup --backup_id <backup_id>`

### Query

- Query: `weaviatest.py query --class_name <class_name> --query <query>`

You can run the Weaviatest CLI directly from the command line.

## Requirements

The Weaviatest CLI requires the following dependencies, which are listed in the `requirements.txt` file. If the required client changes are not yet published, you can use a branch from the `weaviate-python-client` repository. To do so, add the following requirement to the `requirements.txt` file:

```
weaviate-client @ git+https://github.com/weaviate/weaviate-python-client.git@<branch>
```

For example:

```
weaviate-client @ git+https://github.com/weaviate/weaviate-python-client.git@dev/1.26
```

Then, run the following command to install the dependencies:

```
pip install -r requirements.txt
```

## Examples

Here are some examples of how to use the Weaviatest CLI:

1. Create a multitenant class named `Films` with an RF of 3 and an HNSW vector index with PQ enabled (without a vectorizer). Then, add 100 tenants, add 100 objects per tenant with a consistency level of ONE, update all 100 tenants from HOT to COLD, delete 50 tenants, perform a backup, move all remaining tenants back to HOT, update 50 objects for each tenant with a consistency level of ALL, delete the class, and restore the backup:

```
weaviatest.py create class --class_name "Films" --multitenant --vector_index hnsw_pq --replication_factor 3
weaviatest.py create tenants --class_name "Films" --number_tenants 100
weaviatest.py create data --class_name "Films" --number_objects 100 --consistency_level one --randomize
weaviatest.py update tenants --class_name "Films" --number_tenants 100 --state cold
weaviatest.py delete tenants --class_name "Films" --number_tenants 50
weaviatest.py create backup --backup_id "my-films-backup" --wait
weaviatest.py update tenants --class_name "Films" --number_tenants 50 --state hot
weaviatest.py update data --class_name "Films" --number_objects 50 --consistency_level all
weaviatest.py delete class --class_name "Films"
weaviatest.py restore backup --backup_id "my-films-backup" --wait
```

