#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
import aws_cdk as cdk

from cdk.stack import CFDestroyer
from cdk.example_stack import CFDestroyerTest


account = os.getenv("CDK_DEFAULT_ACCOUNT")
region = os.getenv("CDK_DEFAULT_REGION")
schedule = os.getenv("DESTROYER_SCHEDULE")

app = cdk.App()
CFDestroyer(
    app,
    "CFDestroyer",
    env=cdk.Environment(account=account, region=region),
)
test_stack = CFDestroyerTest(
    app,
    "CFTest",
    env=cdk.Environment(account=account, region=region),
)
test_stack.tags.set_tag(
    "STACK_RETENTION", str(cdk.Duration.minutes(1).to_milliseconds())
)
test_stack.tags.set_tag(
    "STACK_EXPIRY", (datetime.now() - timedelta(hours=3)).isoformat()
)
app.synth()
