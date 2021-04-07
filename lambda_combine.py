def lambda_handler(event, context):
    print(event)
    return "Together Ernie and Bert say '{}'!!".format(' '.join(event["input"]))
