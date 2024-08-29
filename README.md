# Weaviatest CLI

CLI tool to perform different Weaviate operations seamlessly. The Weaviatest CLI allows you to create, delete, update, restore, and query various entities in Weaviate.

## Usage

The Weaviatest CLI provides the following actions:

### Create

- Create a collection: `weaviatest.py create collection --collection <collection> --multitenant --vector_index <vector_index> --replication_factor <replication_factor>`
- Create data: `weaviatest.py create data --collection <collection> --limit <limit> --consistency_level <consistency_level> --randomize`
- Create tenants: `weaviatest.py create tenants --collection <collection> --number_tenants <number_tenants>`
- Create backup: `weaviatest.py create backup --backup_id <backup_id>`

### Update

- Update collection: `weaviatest.py update collection --collection <collection> --new_collection <new_collection>`
- Update tenants: `weaviatest.py update tenants --collection <collection> --number_tenants <number_tenants> --state <state>`
- Update data: `weaviatest.py update data --collection <collection> --limit <limit> --consistency_level <consistency_level>`

### Delete

- Delete collection: `weaviatest.py delete collection --collection <collection>`
- Delete data: `weaviatest.py delete data --collection <collection>`
- Delete tenants: `weaviatest.py delete tenants --collection <collection> --number_tenants <number_tenants>`

### Restore

- Restore backup: `weaviatest.py restore backup --backup_id <backup_id>`

### Query

- Query: `weaviatest.py query --collection <collection> --query <query>`

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

1. Create a multitenant collection named `Films` with an RF of 3 and an HNSW vector index with PQ enabled (without a vectorizer). Then, add 100 tenants, add 100 objects per tenant with a consistency level of ONE, update all 100 tenants from HOT to COLD, delete 50 tenants, perform a backup, move all remaining tenants back to HOT, update 50 objects for each tenant with a consistency level of ALL, delete the collection, and restore the backup:

```
weaviatest.py create collection --collection "Films" --multitenant --vector_index hnsw_pq --replication_factor 3
weaviatest.py create tenants --collection "Films" --number_tenants 100
weaviatest.py create data --collection "Films" --limit 100 --consistency_level one --randomize
weaviatest.py update tenants --collection "Films" --number_tenants 100 --state cold
weaviatest.py delete tenants --collection "Films" --number_tenants 50
weaviatest.py create backup --backup_id "my-films-backup" --wait
weaviatest.py update tenants --collection "Films" --number_tenants 50 --state hot
weaviatest.py update data --collection "Films" --limit 50 --consistency_level all
weaviatest.py delete collection --collection "Films"
weaviatest.py restore backup --backup_id "my-films-backup" --wait
```

## Docker image

To build the Docker image for the Weaviatest CLI, follow these steps:

1. Open a terminal and navigate to the root directory of the Weaviatest project.

2. Run the following command to build the Docker image:

    ```
    docker build -t weaviatest .
    ```

    This command will build the Docker image with the tag `weaviatest`.

## Running the application using Docker

To run the Weaviatest CLI application using Docker, follow these steps:

1. Open a terminal.

2. Run the following command to create a collection using the Weaviatest CLI:

    ```
    docker run weaviatest create collection --collection <collection> --multitenant --vector_index <vector_index> --replication_factor <replication_factor>
    ```

    Replace `<collection>`, `<vector_index>`, and `<replication_factor>` with the desired values for your collection.

    You can use similar commands to run other actions provided by the Weaviatest CLI. Just replace `create collection` with the desired action and provide the required parameters.

    For example, to create data, use the following command:

    ```
    docker run weaviatest create data --collection <collection> --limit <limit> --consistency_level <consistency_level> --randomize
    ```

    Replace `<collection>`, `<limit>`, `<consistency_level>`, and `<randomize>` with the desired values for your data creation.

    Note: Make sure you have the Docker daemon running before executing these commands. The application will detect if your docker container is running on MacOS and use `host.docker.internal` as host (otherwise the containerized application won't be able to communicate with `localhost`).

3. If you face issues with the `docker run` command not being able to reach `localhost:8080` (either you are running on a Linux OS or your Docker desktop on Mac has a special network configuration) you will need to pass the `--network=host` option and run all commands like this:

    ````
    docker run --network=host weaviatest create collection
    docker run --network=host weaviatest create data
    docker run --network=host weaviatest delete collection
    ```
