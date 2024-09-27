from iam_role_and_policy import create_role, attach_policy_to_role
from iam_user import create_user, create_access_keys
from s3_operations import assume_role, create_bucket, upload_text_file, upload_binary_file, list_objects_with_prefix, delete_objects_and_bucket
import boto3
import json
import time

session = boto3.Session()
iam_client = session.client('iam')
# Create Dev and User roles
dev_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            'Principal': {'Service': 'ec2.amazonaws.com'},
        }
    ]
}

user_policy = dev_policy

create_role('Dev', dev_policy)
create_role('User', user_policy)

# Attach Policies to Roles
attach_policy_to_role('Dev', 'arn:aws:iam::aws:policy/AmazonS3FullAccess')
attach_policy_to_role('User', 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess')

# Create an IAM user and its access key
user_name = 'TestUser'
create_user(user_name)
access_key_id, secret_access_key = create_access_keys(user_name)
print(access_key_id)
print(secret_access_key)

time.sleep(10)
# Attach the policy to 'TestUser'
iam_client.attach_user_policy(
    UserName='TestUser',
    PolicyArn='arn:aws:iam::aws:policy/IAMFullAccess'
)

# Update the trust policy of the 'Dev' role to allow 'TestUser' to assume the role
dev_trust_policy_update = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Principal': {
                'AWS': f'arn:aws:iam::{session.client("sts").get_caller_identity()["Account"]}:user/TestUser'
            },
            'Action': 'sts:AssumeRole'
        }
    ]
}

iam_client.update_assume_role_policy(
    RoleName='Dev',
    PolicyDocument=json.dumps(dev_trust_policy_update)
)

# Attach an inline policy to 'TestUser'
user_assume_role_policy = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Action': 'sts:AssumeRole',
            'Resource': f'arn:aws:iam::{session.client("sts").get_caller_identity()["Account"]}:role/Dev'
        }
    ]
}

iam_client.put_user_policy(
    UserName='TestUser',
    PolicyName='AllowAssumeDevRole',
    PolicyDocument=json.dumps(user_assume_role_policy)
)

# Initialize session with the IAM user credentials
user_session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
)

time.sleep(10)

# Assume the Dev role and perform S3 operations
dev_role_arn = f"arn:aws:iam::941377123459:role/Dev"
dev_session = assume_role(user_session, dev_role_arn, 'DevSession')

s3_client = dev_session.client('s3')
bucket_name = 'lecture1-weihao'
create_bucket(s3_client, bucket_name)

# perform S3 operations
upload_text_file(s3_client, bucket_name, 'assignment1.txt', 'Empty Assignment 1')
upload_text_file(s3_client, bucket_name, 'assignment2.txt', 'Empty Assignment 2')

upload_binary_file(s3_client, bucket_name, 'cat.jpg', 'cat.jpg')


# For user
# Update the trust policy of the 'User' role to allow 'TestUser' to assume the role
user_trust_policy_update = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Principal': {
                'AWS': f'arn:aws:iam::{session.client("sts").get_caller_identity()["Account"]}:user/TestUser'
            },
            'Action': 'sts:AssumeRole'
        }
    ]
}

iam_client.update_assume_role_policy(
    RoleName='User',
    PolicyDocument=json.dumps(user_trust_policy_update)
)

# Attach an inline policy to 'TestUser'
user_assume_role_policy = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Action': 'sts:AssumeRole',
            'Resource': f'arn:aws:iam::{session.client("sts").get_caller_identity()["Account"]}:role/User'
        }
    ]
}

iam_client.put_user_policy(
    UserName='TestUser',
    PolicyName='AllowAssumeDevRole',
    PolicyDocument=json.dumps(user_assume_role_policy)
)

# Initialize session with the IAM user credentials
user_session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
)
time.sleep(10)
# Assume the User role and perform S3 operations
user_role_arn = f"arn:aws:iam::941377123459:role/User"
dev_session = assume_role(user_session, user_role_arn, 'DevSession')
s3_client = dev_session.client('s3')

list_objects_with_prefix(s3_client, bucket_name, 'assignment')

time.sleep(10)
# Assume the Dev role again and delete all objects and the bucket
dev_role_arn = f"arn:aws:iam::941377123459:role/Dev"
dev_session = assume_role(user_session, dev_role_arn, 'DevSession2')
s3_client = dev_session.client('s3')
delete_objects_and_bucket(s3_client, bucket_name)