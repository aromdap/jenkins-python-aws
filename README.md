# todo-list-aws

This project is split in different parts:
1. Build and deploy todo-list app in Serverless Framework via Github repository
2. Implement new feature in Python to translate any of the inputs stored in DynamoDB
3. Migrate Github repository to AWS CodeCommit
4. Migrate app project from Serverless Framework to SAM Framework 
5. Run SAM locally with DynamoDB instance in a Docker Network
6. Operate and test manually that all endpoints work as expected
7. SAM Build & SAM Deploy to AWS
8. Operate and test manually that all endopoints work as expected

### The application: A simple Python to-do-list

The app has a series of funcions that will interact with the user through an API. In this case, since we are working on an AWS context, an API Gateway.

The following are the functions that this app will have:
- Create
- List
- Get
- Update
- Translate 
- Delete

The function translate is based on the Comprehend and Tranlate natural language processing frameworks.

You can get to know more about these AWS technologies [here](https://docs.aws.amazon.com/translate/latest/dg/what-is.html).

## AWS architecture

The following AWS components are the ones that will compose the ecosystem of our application:
- SAM 
- API gateway
- Lambda functions
- DynamoDB
- EC2
- IAM 

Each of them will have a function in our project
* SAM: being our engine to build and deploy the application
* API gateway: being the link to address the request to our application
* Lambda: they will wrap our functions
* DynamoDB: will store the information of our list
* EC2: will be the instance of our serverless project
* IAM: will be managing security credentials


## Introduction: Serverless Framework

This project aims at deploying a Pyhton app in its function-based structure in a Serverless Framework . Since the cloud provided is AWS, the template.yaml will have to declare in conjunction with our provided.

Before doing so, we recommend to go through the [Serverless Framework documentation](https://www.serverless.com/framework/docs/providers/aws/)


![alt text](https://www.google.com/url?sa=i&url=https%3A%2F%2Fdev.to%2Fmquanit%2Fcreate-deploy-your-first-ever-aws-lambda-function-by-serverless-framework-2hga&psig=AOvVaw31GpyZ60Jr5knbri59Sfqq&ust=1613163442801000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCKDxp6ve4u4CFQAAAAAdAAAAABAD)

### Serverless Framework: first steps

Install the serverless CLI:
```
npm install -g serverless
```

Run below command and follow the prompts
```
serverless
```

Once you’ve signed up for Pro, login to your Pro dashboard from the CLI:
```
serverless login
```

### The deployment:

The template.yaml will help to properly deploy the application into an AWS EC2 instance when building a simple pipeline.

In this case, two pipelines should be built in order to cover the staging and the production environments, that will match with the Master and Develop branches of the GitHub repository.

Anytime a pull request is done against any of the branches, it will trigger the automated build and deployment of the app.

## Switching to SAM

At this stage of the exercise, we are migrating from Serverless Framework to SAM Serverless.

The template will have to be adapted to accommodate it to SAM standards.

SAM will be the platform that will help us to build and deploy the application to AWS.

You can get more of a taste in the following links:
**Detailed References:** Explains SAM commands and usage in depth.
* [CLI Commands](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)
* [SAM Template Specification](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification.html)
* [Policy Templates](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-templates.html)

## SAM used in a local context

We will deploy SAM locally, against a DynamoDB instance in a Docker container. This will allow us to test our endpoints without the need of consuming AWS resources, at least until having a stable version.

We assume that you have installed Docker and Docker-Compose in your machine before you move forward any furhter.

To achive the local deployment you will need to work a wee bit on the CLI in order to:
1. Create a Docker Network
```
docker network create local-todo-list
```
2. Do a docker-compose up to create the DynamoDB instance
```
docker-compose up
```
3. Create manually the table in the DynamoDB instance (look at dynamo-table-template.json)
```
aws dynamodb create-table --table-name 'TodoListTable' --cli-input-json file://dynamo-table-template.json --endpoint-url http://localhost:8000
```
4. Check that the table exists
```
aws dynamodb list-tables --endpoint-url http://localhost:8000
```
5. Build with SAM
```
sam build
```
6. Deploy locally, providing the parameters: **DynamoDbTable and Stage**
```
sam build && sam local start-api --docker-network local-todo-list --parameter-overrides ParameterKey=DynamoDbTable,ParameterValue=TodoListTable ParameterKey=Stage,ParameterValue=local
```

The constructor of the Python class for the app will build the DynamoDB resource based on the local environment variable value. Also, pay attention to the endpoint_url: it matches with the one declared in the **docker-compose.yml**.
```
if os.getenv('STAGE') == 'local':
            self.dynamodb = boto3.resource('dynamodb',
                                           endpoint_url='http://dynamodb:8000')
        else:
            self.dynamodb = boto3.resource('dynamodb')
```

### Test your endpoints

There you go, this is for free:
```
curl -X POST http://127.0.0.1:3000/create --data '{ "text": "Learn Serverless" }'
```
**Response:**
{"id": "aefcdd41-64b1-11eb-af9f-a9da7a8c1ae2", "text": "Learn Serverless", "checked": false, "createdAt": "1612199987.2451952", "updatedAt": "1612199987.2451952"}

```
curl https://127.0.0.1:3000/show 
```
**Response:**
[{"checked": false, "createdAt": "1612199987.2451952", "id": "aefcdd41-64b1-11eb-af9f-a9da7a8c1ae2", "text": "Learn Serverless", "updatedAt": "1612199987.2451952"}]

```
curl https://127.0.0.1:3000/get/<id>
```
**Response:**
{"checked": false, "createdAt": "1612199987.2451952", "id": "aefcdd41-64b1-11eb-af9f-a9da7a8c1ae2", "text": "Learn Serverless", "updatedAt": "1612199987.2451952"}
```
curl -X PUT https://127.0.0.1:3000/update/<id> --data '{ "text": "Learn Serverless", "checked": true }'
```
**Response:**
{"createdAt": "1612199987.2451952", "checked": true, "id": "aefcdd41-64b1-11eb-af9f-a9da7a8c1ae2", "text": "Learn Serverless", "updatedAt": 1612200254004}
```
curl -X DELETE https://127.0.0.1:3000/delete/<id>
```
**Response:**
"Deleted ID: aefcdd41-64b1-11eb-af9f-a9da7a8c1ae2"

## SAM Deploy: now for real

Once you are sure your endpoints behave as expected, deploy manually your application using the guided option:
```
sam deploy --guided
```

The outcome of that command will generate a file similar to the **samconfig.toml** but only with a [default] profile. This file is really important: you will later define your staging and production indications for the deployments via Jenkins.

## Jenkins: serious business now

It is time to automate your deployment, and it will be done by composing three pipelines that will do the work for you:
- **Pipeline - Staging: it will deploy your code held in the dev branch**
* Stage - Checkout
* Stage - Setup
* Stage - Code analysis
* Stage - Unit test
* Stage - Build
* Stage - Deploy
* Stage - Functional test
* Stage - Merge to master
* Stage - Clean after yourself
- **Pipeline - Production: it will deploy your code held in the main branch**
* Stage - Checkout
* Stage - Setup
* Stage - Build
* Stage - Deploy
* Stage - Functional test
* Stage - Clean after yourself
- **Pipeline - Full CICD: it will trigger sequently the two pipelines**
* Stage - Staging
* Stage - Production

### Testing: minimums

For the testing, some minimums are requested:
- **Code static analysis:**
* Radon: No ranks above B in the analysis code will be allowed
* Flake8: No errors in PEP8 standars will be allowed
* Bandit: No errors will be allowed

- **Unit test:**
* Pytest or Unittest modules will pass unit test on class methods
* Coverage will have to be up to 80%

- **Functional testing:**
* All endpoints have to work
* Control the outputs of all requests to methods and fail if unexpected behaviour is detected



