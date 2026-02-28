"""DatabaseStack — VPC + Aurora Serverless v2 (PostgreSQL-compatible).

Deploy this stack first and let it stabilise before deploying AppStack.
The cluster and secret have RETAIN removal policies so they survive a
stack delete during blue/green cut-overs.
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class DatabaseStack(Stack):
    """VPC + Aurora Serverless v2 PostgreSQL cluster."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── VPC ────────────────────────────────────────────────────────────
        # Two AZs, private subnets for the DB (Lambda will sit here too),
        # public subnets for the NAT gateway so Lambda can reach Secrets
        # Manager and other AWS APIs.
        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        # ── Security group for the Aurora cluster ──────────────────────────
        self.db_security_group = ec2.SecurityGroup(
            self,
            "DbSg",
            vpc=self.vpc,
            description="Aurora Serverless v2 — allow PostgreSQL from within VPC",
            allow_all_outbound=False,
        )
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5432),
            description="PostgreSQL from VPC",
        )

        # ── Aurora Serverless v2 cluster ───────────────────────────────────
        self.cluster = rds.DatabaseCluster(
            self,
            "Cluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_16_6,
            ),
            # Serverless v2 writer instance — scales to 0 ACUs when idle
            writer=rds.ClusterInstance.serverless_v2(
                "Writer",
                auto_pause=rds.TimeoutAction.force_apply_server_side_timeout(),
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.db_security_group],
            default_database_name="earthborne",
            # Serverless v2 capacity: 0.5 → 4 ACUs (free tier friendly)
            serverless_v2_min_capacity=0.5,
            serverless_v2_max_capacity=4,
            # Keep cluster and its auto-generated secret alive on stack delete
            removal_policy=cdk.RemovalPolicy.RETAIN,
            storage_encrypted=True,
            backup=rds.BackupProps(retention=cdk.Duration.days(7)),
            deletion_protection=True,
        )

        # ── Expose outputs for AppStack ────────────────────────────────────
        # The cluster secret holds {host, port, dbname, username, password}.
        self.db_secret: secretsmanager.ISecret = self.cluster.secret  # type: ignore[assignment]

        cdk.CfnOutput(self, "ClusterEndpoint", value=self.cluster.cluster_endpoint.hostname)
        cdk.CfnOutput(self, "DbSecretArn", value=self.db_secret.secret_arn)
