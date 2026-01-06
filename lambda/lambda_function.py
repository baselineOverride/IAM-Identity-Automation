import csv
import boto3
import logging
import os

logger = logging.getLogger()

s3 = boto3.client('s3') 
iam = boto3.client('iam')

GROUPS = {
    'dev': 'Developer-Team',
    'security': 'Security-Team',
    'readonly': 'Read-Only'   
}

def lambda_handler(event, context):
    # Get bucket & object key from S3 event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    logger.info("Processing file %s", key)

    # Get Object 
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8').splitlines()

    # Parse body of CSV
    csv_reader = csv.DictReader(data)

    for row in csv_reader:
        username = row['username'].strip()
        position = row['position'].strip()
        mode = row['mode'].strip()

        if mode == 'add':
            add_user(username, position)
        elif mode == 'remove':
            remove_user(username)
        elif mode == 'move':
            move_user(username, position)
        else:
           logger.error("Invalid operation: %s", mode) 

    return "Success"


def add_user(username, position):
    group = GROUPS.get(position)

    # Error Handling
    if not group:
        logger.error("Invalid group: %s", position)
        return
    
    # Check User exists, if not create
    try:
        iam.get_user(UserName=username)
        logger.info("User %s already exists", username)
    except iam.exceptions.NoSuchEntityException:
        logger.info("Creating user %s", username)
        iam.create_user(UserName=username)

    # Try adding user to group
    try:
        iam.add_user_to_group(GroupName=group, UserName=username)
        logger.info("Adding user %s to group %s", username, group)
    except iam.exceptions.EntityAlreadyExistsException:
        logger.info("User %s already in group %s", username, group)

def move_user(username, position):
    new_group = GROUPS.get(position)

    # Error Handling
    if not new_group:
        logger.error("Invalid group: %s", position)
        return

    # Remove user from all groups
    for group in GROUPS.values():
        try:
            iam.remove_user_from_group(GroupName=group, UserName=username)
            logger.info("Removing user %s from group %s", username, group)
        except iam.exceptions.NoSuchEntityException:
            logger.info("User %s not in group %s", username, group)

    # Try adding user to group
    try:
        iam.add_user_to_group(GroupName=new_group, UserName=username)
        logger.info("Adding user %s to group %s", username, new_group)
    except iam.exceptions.EntityAlreadyExistsException:
        logger.info("User %s already in group %s", username, new_group)

def remove_user(username):
    # Check User exists
    try:
        iam.get_user(UserName=username)
    except iam.exceptions.NoSuchEntityException:
        logger.info("User %s does not exist", username)
        return

    # Remove user from all groups
    # Provides safe exits - Removes User after they are removed from all groups
    for group in GROUPS.values():
        try:
            iam.remove_user_from_group(GroupName=group, UserName=username)
            logger.info("Removing user %s from group %s", username, group)
        except iam.exceptions.NoSuchEntityException:
            logger.info("User %s not in group %s", username, group)

    # Delete user
    iam.delete_user(UserName=username)
    logger.info("Deleting user %s", username)
    	    