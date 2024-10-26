# utils/dynamodb_utils.py

from botocore.exceptions import ClientError

def get_all_dynamodb_items(table):
    """
    Retrieve all items from a DynamoDB table.

    This function scans the specified DynamoDB table and retrieves all items.
    It handles pagination in case the table contains more items than can be 
    returned in a single scan request.

    Parameters:
    table (boto3.resources.factory.dynamodb.Table): The DynamoDB table resource 
    from which to retrieve items.

    Returns:
    list: A list of items retrieved from the DynamoDB table. Each item is a 
    dictionary representing a single record.

    Raises:
    ClientError: If the scan operation fails, a ClientError is raised, and an 
    error message is printed.
    """

    items = []
    try:
        response = table.scan()
        items.extend(response.get('Items', []))

        # Handle pagination in case there are more items to retrieve
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

    except ClientError as e:
        print(f"Failed to get items from DynamoDB: {e.response['Error']['Message']}")

    return items