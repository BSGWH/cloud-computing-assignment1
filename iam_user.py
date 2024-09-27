import boto3


def create_user(user_name):
    iam_client = boto3.client('iam')
    user = iam_client.create_user(UserName=user_name)
    print(f"User '{user_name}' created successfully.")
    return user


def create_access_keys(user_name):
    iam_client = boto3.client('iam')
    access_key_pair = iam_client.create_access_key(UserName=user_name)
    print(f"Access keys created for user '{user_name}'.")
    return access_key_pair['AccessKey']['AccessKeyId'], access_key_pair['AccessKey']['SecretAccessKey']


