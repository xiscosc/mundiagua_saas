from boto3.dynamodb.conditions import Key, Attr

from core.aws.aws_client import create_amazon_resource


def dynamodb_store_item(table_name: str, item: dict):
    c = create_amazon_resource('dynamodb')
    c.Table(table_name).put_item(Item=item)


def dynamodb_get_item(table_name: str, partition_key: str, sort_key: str, partition_key_name,
                      sort_key_name) -> dict | None:
    c = create_amazon_resource('dynamodb')
    table = c.Table(table_name)
    k = {
        sort_key_name: sort_key,
        partition_key_name: partition_key
    }
    response = table.get_item(Key=k)
    if 'Item' in response:
        return response['Item']
    else:
        return None


def dynamodb_delete_item(table_name: str, partition_key: str, sort_key: str, partition_key_name, sort_key_name):
    c = create_amazon_resource('dynamodb')
    table = c.Table(table_name)
    k = {
        sort_key_name: sort_key,
        partition_key_name: partition_key
    }

    table.delete_item(Key=k)


def dynamodb_get_items(table_name: str, partition_key: str, partition_key_name, filter_exp: dict | None) -> list[dict]:
    c = create_amazon_resource('dynamodb')
    table = c.Table(table_name)
    if not filter_exp:
        response = table.query(KeyConditionExpression=Key(partition_key_name).eq(partition_key))
    else:
        response = table.query(
            KeyConditionExpression=Key(partition_key_name).eq(partition_key),
            FilterExpression=Attr(filter_exp['field']).eq(filter_exp['value'])
        )
    return response['Items']
