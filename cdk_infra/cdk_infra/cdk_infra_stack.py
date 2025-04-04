from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3, aws_dynamodb as dynamodb
from constructs import Construct

class MinimalStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # S3 Bucket
        s3.Bucket(self, "WebcameraTestBucket",
            bucket_name="webcamera-dev-test-123",
            versioned=True,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Customers Table
        dynamodb.Table(self, "CustomersTableTest",
            table_name="customersTest",
            partition_key=dynamodb.Attribute(
                name="email",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Products table
        dynamodb.Table(self, "ProductsTableTest",
            table_name="productsTest",
            partition_key=dynamodb.Attribute(
                name="product_name",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Purchases table
        dynamodb.Table(self, "PurchasesTableTest",
            table_name="purchasesTest",
            partition_key=dynamodb.Attribute(
                name="customer_email",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="purchase_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
