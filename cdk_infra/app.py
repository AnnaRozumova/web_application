import aws_cdk as cdk
from stack import MinimalStack

app = cdk.App()
MinimalStack(app, "MinimalStack")
