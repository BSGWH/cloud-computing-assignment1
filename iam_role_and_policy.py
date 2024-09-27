import boto3
import json


def create_role(role_name, trust_policy):
    # Allow python to interact with IAM
    iam_client = boto3.client('iam')
    role = iam_client.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy))
    print(f"Role '{role_name}' created successfully.")
    return role


def attach_policy_to_role(role_name, policy_arn):
    iam_client = boto3.client('iam')
    iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    print(f"Policy '{policy_arn}' attached to role '{role_name}'.")

