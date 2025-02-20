# aws-step-function
Small repo to demonstrate a step function implementation.

## Set some environment variables
```shell
export AWS_ACCOUNT_ID=[ENTER AWS ACCOUNT ID HERE]
export AWS_PAGER=""
export LAMBDA_ROLE=lambda-execution
export AWS_REGION=us-east-1
export STEP_ROLE=step-execution
```

## Create Roles
Both the Lambda and Step Function execution roles require a trust policy file that allowes
it to assume the associated service. These `*-trust-policy.json` files are in the root of
this repo.

### Create Lambda Function Role
Create the Lambda role and attach the `AWSLambdaBasicExecutionRole` policy to the new 
Lambda role to allow basic execution. 
```shell
aws iam create-role --role-name $LAMBDA_ROLE \
--assume-role-policy-document file://lambda-trust-policy.json
aws iam attach-role-policy --role-name $LAMBDA_ROLE \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Create Step Function Role
Create a Step Function execution role and attached the `AWSLambdaRole` policy to the new 
Step Function role to allow the step function to invoke Lambda functions. 
```shell
aws iam create-role --role-name $STEP_ROLE \
--assume-role-policy-document file://step-trust-policy.json
aws iam attach-role-policy --role-name $STEP_ROLE \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaRole
```

## Create three Lambda functions populate the step function 
The following commands will create the three simple lambda functions.
```shell
cp -f lambda_ernie.py lambda_function.py
zip package.zip lambda_function.py
aws lambda create-function \
--function-name ernie \
--role arn:aws:iam::${AWS_ACCOUNT_ID}:role/$LAMBDA_ROLE \
--runtime python3.13 --timeout 10 --memory-size 128 \
--handler lambda_function.lambda_handler \
--zip-file fileb://package.zip
rm package.zip lambda_function.py

cp -f lambda_bert.py lambda_function.py
zip package.zip lambda_function.py
aws lambda create-function \
--function-name bert \
--role arn:aws:iam::${AWS_ACCOUNT_ID}:role/$LAMBDA_ROLE \
--runtime python3.13 --timeout 10 --memory-size 128 \
--handler lambda_function.lambda_handler \
--zip-file fileb://package.zip
rm package.zip lambda_function.py

cp -f lambda_combine.py lambda_function.py
zip package.zip lambda_function.py
aws lambda create-function \
--function-name combine \
--role arn:aws:iam::${AWS_ACCOUNT_ID}:role/$LAMBDA_ROLE \
--runtime python3.13 --timeout 10 --memory-size 128 \
--handler lambda_function.lambda_handler \
--zip-file fileb://package.zip
rm package.zip lambda_function.py
```

It may also be useful to update the package through the CLI with the following command.
```shell
cp -f lambda_ernie.py lambda_function.py
zip package.zip lambda_function.py
aws lambda update-function-code --function-name  ernie --zip-file fileb://package.zip
rm package.zip lambda_function.py
```

## Create the State Machine (Step Function)
The step function definition file `step-definition.json` in this repo has placeholders for 
the AWS account number and region. These are replaced by envirinment variables by a sed 
command to make a temp file. This temp file is then piped into the CLI command to make the 
step function.
```shell
sed "s/AWS_REGION/${AWS_REGION}/;s/AWS_ACCOUNT_ID/${AWS_ACCOUNT_ID}/" step-definition.json > temp.json
aws stepfunctions create-state-machine --name step-demo \
--definition "$(cat temp.json)" \
--role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/$STEP_ROLE
rm -f temp.json
```
This creates the flow between the three lambda functions as illustrated below.   
![step](stepfunctions_graph.png)


## Invoke the step function
The following command invokes the step function.
```shell
aws stepfunctions start-execution \
--state-machine-arn arn:aws:states:${AWS_REGION}:${AWS_ACCOUNT_ID}:stateMachine:step-demo \
--input '{"ernie": "oh", "bert": "snap"}'
```
You should see the following in the AWS State Machine console under the step function 
execution grap details.
![step2](stepfunctions_output.png)

## References
- [AWS SAM Repo](https://github.com/daniel-fudge/aws-sam-test)
- [AWS S3-Trigger Repo](https://github.com/daniel-fudge/aws-s3-trigger)
- [AWS CLI - Installation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html)
- [AWS CLI - Add permissions](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-permission.html)
- [AWS CLI - Invoke Lambda](https://docs.aws.amazon.com/cli/latest/reference/lambda/invoke.html#examples)
- [AWS S3 API](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3api/put-bucket-notification-configuration.html)
- [AWS Step Output Filter](https://docs.aws.amazon.com/step-functions/latest/dg/input-output-example.html)
- [AWS Lambda Runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)
