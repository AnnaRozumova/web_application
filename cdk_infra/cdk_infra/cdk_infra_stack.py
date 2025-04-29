"""CDK infrastructure module for deploying S3 bucket, 
DynamoDB tables, Lambda function, and API Gateway."""
import json
from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3, aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigateway
from constructs import Construct

class MinimalStack(Stack):
    '''CDK Stack'''
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # S3 Bucket
        s3.Bucket(self, "WebcameraBucket",
            bucket_name="webcamera-app-dev-65t20mo50",
            versioned=True,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Customers Table
        dynamodb.Table(self, "CustomersTable",
            table_name="customers",
            partition_key=dynamodb.Attribute(
                name="email",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Products table
        dynamodb.Table(self, "ProductsTable",
            table_name="products",
            partition_key=dynamodb.Attribute(
                name="product_name",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Purchases table
        dynamodb.Table(self, "PurchasesTable",
            table_name="purchases",
            partition_key=dynamodb.Attribute(
                name="customer_email",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="purchase_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        purchases_table = dynamodb.Table.from_table_name(self, "PurchasesTableRef", "purchases")

        search_lambda = _lambda.Function(
            self, "DBSearchLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="src.lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/db_search_app/dist"),
            environment={
                "PURCHASES_TABLE_NAME": "purchases"
            }
        )

        purchases_table.grant_read_data(search_lambda)

        api = apigateway.RestApi(self, "PurchasesAPI",
                                rest_api_name="Purchases Service",
                                description="Simple API to query purchases.")
        purchases_resource = api.root.add_resource("purchases")

        get_details = purchases_resource.add_resource("get_purchase_details")
        get_details.add_method(
            "GET",
            apigateway.LambdaIntegration(
                search_lambda,
                proxy=False,
                integration_responses=[{"statusCode": "200"}],
                request_templates={
                    "application/json": json.dumps({
                        "action": "get_purchase_details",
                        "customer_email": "$input.params('email')"
                    })
                }
            ),
            method_responses=[{
                "statusCode": "200"
            }],
            request_parameters={
                "method.request.querystring.email": True
            }
        )

        get_all = purchases_resource.add_resource("get_all_purchases")
        get_all.add_method(
            "GET",
            apigateway.LambdaIntegration(
                search_lambda,
                proxy=False,
                integration_responses=[{
                    "statusCode": "200"
                }],
                request_templates={
                    "application/json": json.dumps({
                        "action": "get_all_purchases"
                    })
                }
            ),
            method_responses=[{
                "statusCode": "200"
            }]
        )
