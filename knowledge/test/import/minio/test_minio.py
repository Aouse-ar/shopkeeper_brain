import os
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error

load_dotenv()


def main():
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    client = Minio(os.getenv("MINIO_ENDPOINT", "192.168.200.130:9000"),
                   access_key=os.getenv("MINIO_ACCESS_KEY"),
                   secret_key=os.getenv("MINIO_SECRET_KEY"),
                   secure=False
                   )

    source_file = "C:\\Users\\32278\\Desktop\\5828d3f3c4b69fb74b2c4dde171472c0.jpg"

    bucket_name = "test"
    destination_file = "temp_0.jpg"

    # Make the bucket if it doesn't exist.
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    client.fput_object(
        bucket_name, destination_file, source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
