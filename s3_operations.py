import boto3

def assume_role(session, role_arn, session_name):
    sts_client = session.client('sts')
    assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
    credentials = assumed_role['Credentials']
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

def create_bucket(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' created.")



def upload_text_file(s3_client, bucket_name, key, content):
    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=content
    )
    print(f"Uploaded text file '{key}' to bucket '{bucket_name}'.")

def upload_binary_file(s3_client, bucket_name, key, file_path):
    with open(file_path, 'rb') as file_data:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=file_data
        )
    print(f"Uploaded binary file '{key}' to bucket '{bucket_name}'.")

def list_objects_with_prefix(s3_client, bucket_name, prefix):
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix
    )
    objects = response.get('Contents', [])
    total_size = sum(obj['Size'] for obj in objects)
    print(f"Total size of objects with prefix '{prefix}': {total_size} bytes")
    return objects, total_size

def delete_objects_and_bucket(s3_client, bucket_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    objects = response.get('Contents', [])
    for obj in objects:
        s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
        print(f"Deleted object '{obj['Key']}' from bucket '{bucket_name}'.")
    s3_client.delete_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' deleted.")