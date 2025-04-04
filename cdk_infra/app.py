import aws_cdk as cdk
from cdk_infra.cdk_infra_stack import MinimalStack


app = cdk.App()
MinimalStack(app, "MinimalStack")

app.synth()
