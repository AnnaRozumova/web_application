from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3, aws_dynamodb as dynamodb
from constructs import Construct

class MinimalStack(Stack):
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
