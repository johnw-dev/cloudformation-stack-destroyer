from aws_cdk import RemovalPolicy, Stack, Environment
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
from constructs import Construct
import random


class CFDestroyerTest(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env: Environment, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        s3.Bucket(
            self,
            "Bucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
