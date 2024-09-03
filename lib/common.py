import socket
import string
import random
import weaviate


def check_host_docker_internal(port=8080):
    """Check if host.docker.internal is reachable."""
    try:
        # Attempt to connect to host.docker.internal on any port (e.g., 80)
        fd = socket.create_connection(("host.docker.internal", port), timeout=2)
        fd.close()  # Close the socket
        return True
    except (socket.timeout, socket.error):
        return False


def get_host(port):
    """Determine the appropriate host based on the environment."""
    if check_host_docker_internal(port):
        return "host.docker.internal"  # macOS/Windows Docker
    else:
        return "localhost"  # Default fallback (Linux or unreachable)


def connect_to_weaviate(host, api_key, port, grpc_port):
    # Connect to Weaviate instance
    if host == "localhost":
        client = weaviate.connect_to_local(
            host=get_host(port), port=port, grpc_port=grpc_port
        )
    else:
        client = weaviate.connect_to_wcs(
            cluster_url=host,
            auth_credentials=weaviate.auth.AuthApiKey(api_key=api_key),
        )
    return client


# Insert objects to the replicated collection
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


# Pretty print objects in the response in a table format
def pp_objects(response):
    if len(response.objects) == 0:
        print("No objects found")
        return
    print(
        f"{'ID':<37}{'Title':<37}{'Keywords':<37}{'Distance':<11}{'Certainty':<11}{'Score':<11}"
    )
    for obj in response.objects:
        print(
            f'{str(obj.uuid):<36} {obj.properties["title"][:36]:<36} {obj.properties["keywords"][:36]:<36} {obj.metadata.distance if obj.metadata.distance else "None":<10} {obj.metadata.certainty if obj.metadata.certainty else "None":<10} {obj.metadata.score if obj.metadata.score else "None":<10}'
        )
    print(f"{'':<37}{'':<37}{'':<37}{'':<11}{'':<11}{'':<11}")
    print(f"Total: {len(response.objects)} objects")
