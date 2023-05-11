from aws_cdk import Stack, Environment
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_iam as iam
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as targets
from constructs import Construct
import os


def get_cron():
    """
    this function exists because aws decided not to support standard cron
    determine which of day(month) or day(week) to use - defaults to day of month
    """
    schedule = os.getenv("DESTROYER_SCHEDULE").split(" ")
    list(map(lambda x: x if x != "*" else None, schedule))
    if schedule[2] and schedule[4]:
        # aws doesn't support both days and weekdays like cron
        schedule[4] = None
    return schedule


class CFDestroyer(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env: Environment, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        function_role = iam.Role(
            self,
            "FunctionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "allow_pass_role": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["iam:PassRole"],
                            resources=[
                                f"arn:aws:iam::{env.account}:role/rol_cloudformation_stack_destroyer_control"
                            ],
                        ),
                    ],
                ),
                "allow_cf_permissions": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "cloudformation:DeleteStack",
                                "cloudformation:DescribeStackResources",
                            ],
                            resources=[
                                f"arn:aws:cloudformation:{env.region}:{env.account}:stack/*/*",
                                f"arn:aws:cloudformation:{env.region}:{env.account}:stack/*",
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "cloudformation:DescribeStacks",
                                "cloudformation:ListStacks",
                            ],
                            resources=[
                                "*",
                            ],
                        ),
                    ],
                ),
            },
        )
        function_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        function_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole"
            )
        )
        function = _lambda.Function(
            self,
            "Function",
            handler="function.handler.handler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("assets"),
            role=function_role,
        )
        function.add_environment("STACK_RETENTION_TAG", "STACK_RETENTION")
        function.add_environment("STACK_EXPIRY_TAG", "STACK_EXPIRY")

        cron = get_cron()
        rule = events.Rule(
            self,
            "DestroyerSchedule",
            schedule=events.Schedule.cron(
                minute=cron[0],
                hour=cron[1],
                day=cron[2],
                month=cron[3],
                week_day=cron[4],
            ),
        )
        rule.add_target(targets.LambdaFunction(function, retry_attempts=2))
