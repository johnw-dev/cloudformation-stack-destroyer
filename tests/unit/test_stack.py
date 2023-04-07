from aws_cdk import App, Environment
import aws_cdk.assertions as assertions

from cdk.stack import CFDestroyer


# example tests. To run these tests, uncomment this file along with the example
# resource in cloudformation_stack_destroyer/cloudformation_stack_destroyer_stack.py
def test_lambda_created():
    app = App()
    stack = CFDestroyer(
        app,
        "cloudformation-stack-destroyer",
        Environment(region="eu-west-1", account="99999999"),
    )
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"Runtime": "python3.9", "Handler": "function.handler.handler"},
    )
