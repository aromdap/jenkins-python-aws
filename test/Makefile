[local]
	docker network create local-todo-list
	docker network up
	docker-compose up
	aws dynamodb create-table --table-name 'TodoListTable' --cli-input-json file://dynamo-table-template.json --endpoint-url http://localhost:8000
	sam build && sam local start-api --docker-network local-todo-list --parameter-overrides ParameterKey=DynamoDbTable,ParameterValue=TodoListTable ParameterKey=Stage,ParameterValue=local

