"""An AWS Python Pulumi program"""

import pulumi
from pulumi import Config
import pulumi_aws as aws
from pulumi_aws import route53
from pulumi_aws import acm
from pulumi_aws import cloudfront
from pulumi_aws import s3
from pulumi_aws import wafv2

config = Config()
env = pulumi.get_stack()
base_tags = {
    "Environment": env,
    "Project": "GoLab",
    "Owner": "GoLab Team",
    "ManagedBy": "Pulumi",
}

current = aws.s3.get_canonical_user_id()
cloudfront_log_delivery_canonical_user_id = (
    cloudfront.get_log_delivery_canonical_user_id()
)

# Fetch existing R53 zone for golab.com
r53_root_zone_name = config.require("r53_root_zone_name")
r53_root_zone = route53.get_zone(name=r53_root_zone_name)

# Create env specific R53 zone for golab.com
r53_env_zone = route53.Zone(
    "env-zone",
    name=f"{env}.{r53_root_zone_name}",
    tags=base_tags,
)

r53_env_ns_record = route53.Record(
    "env-ns",
    name=env,
    zone_id=r53_root_zone.zone_id,
    type="NS",
    ttl=30,
    records=r53_env_zone.name_servers,
)

# Create ACM certificate for env.golab.com and expected SANs based on env
acm_sans = [f"*.{env}.{r53_root_zone_name}"]  # Wildcard SAN for non-prod envs

if env == "prod":
    acm_sans.extend(
        [
            f"*.{r53_root_zone_name}",  # Wildcard SAN for prod env
            r53_root_zone_name,  # Root domain SAN for prod env
        ]
    )

acm_cert = acm.Certificate(
    "env-cert",
    domain_name=r53_env_zone.name,
    validation_method="DNS",
    subject_alternative_names=[san for san in acm_sans],
    opts=pulumi.ResourceOptions(delete_before_replace=True),
    tags=base_tags,
)

pulumi.export("acm_cert_arn", acm_cert.arn)
pulumi.export("acm_cert_subject_alternative_names", acm_cert.subject_alternative_names)

# Create DNS validation records for ACM certificate
validation_records = acm_cert.domain_validation_options.apply(
    lambda options: [
        route53.Record(
            f"cert_validation_record_{i}",
            name=opt["resource_record_name"],
            type=opt["resource_record_type"],
            records=[opt["resource_record_value"]],
            zone_id=(
                r53_env_zone.zone_id.apply(lambda id: id)
                if f"{r53_env_zone.name.apply(lambda name: name)}" in opt["domain_name"]
                else r53_root_zone.zone_id
            ),
            allow_overwrite=True,  # TODO: Remove this once duplicates are removed from domain_validation_options yuck
            ttl=300,
        )
        for i, opt in enumerate(options)
    ]
)

validation = acm.CertificateValidation(
    "cert-validation",
    certificate_arn=acm_cert.arn,
    validation_record_fqdns=validation_records.apply(
        lambda records: [record.fqdn.apply(lambda fqdn: fqdn) for record in records]
    ),
)

# Create bucket for S3 client logs from each env
if env == "dev":
    s3_log_bucket = s3.Bucket(
        "s3-log-bucket",
        bucket=f"logs.{r53_root_zone_name}",
        lifecycle_rules=[
            s3.BucketLifecycleRuleArgs(
                enabled=True,
                prefix="",
                tags=base_tags,
                transitions=[
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=30,
                        storage_class="ONEZONE_IA",
                    ),
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=60,
                        storage_class="GLACIER",
                    ),
                ],
                expiration=aws.s3.BucketLifecycleRuleExpirationArgs(
                    days=180,
                ),
            )
        ],
        tags=base_tags,
    )

    s3_log_bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "logging.s3.amazonaws.com"},
                "Action": "s3:PutObject",
                "Resource": [s3_log_bucket.arn.apply(lambda arn: f"{arn}/*")],
            }
        ],
    }

    s3_log_bucket_access_policy = (
        s3.BucketPolicy(
            "s3-log-bucket-access-policy",
            bucket=s3_log_bucket.id,
            policy=pulumi.Output.json_dumps(s3_log_bucket_policy),
        ),
    )

    cf_log_bucket = s3.Bucket(
        "cf-log-bucket",
        bucket=f"cf-logs.{r53_root_zone_name}",
        grants=[
            s3.BucketGrantArgs(
                permissions=["WRITE"],
                type="CanonicalUser",
                id=current.id,
            ),
            s3.BucketGrantArgs(
                permissions=["WRITE"],
                type="CanonicalUser",
                id=cloudfront_log_delivery_canonical_user_id.id,
            ),
        ],
        lifecycle_rules=[
            s3.BucketLifecycleRuleArgs(
                enabled=True,
                prefix="",
                tags=base_tags,
                transitions=[
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=30,
                        storage_class="ONEZONE_IA",
                    ),
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=60,
                        storage_class="GLACIER",
                    ),
                ],
                expiration=aws.s3.BucketLifecycleRuleExpirationArgs(
                    days=180,
                ),
            )
        ],
        tags=base_tags,
    )

    cf_log_bucket_object_ownership_rules = s3.BucketOwnershipControls(
        "cf-log-bucket-object-ownership-rules",
        bucket=cf_log_bucket.id,
        rule=s3.BucketOwnershipControlsRuleArgs(
            object_ownership="ObjectWriter",
        ),
    )
else:
    s3_log_bucket = s3.get_bucket(bucket=f"logs.{r53_root_zone_name}")
    cf_log_bucket = s3.get_bucket(bucket=f"cf-logs.{r53_root_zone_name}")

pulumi.export("s3_log_bucket_name", s3_log_bucket.id)
pulumi.export("s3_log_bucket_arn", s3_log_bucket.arn)
pulumi.export("cf_log_bucket_name", cf_log_bucket.id)
pulumi.export("cf_log_bucket_arn", cf_log_bucket.arn)

# Create S3 bucket for static site that will be served by CloudFront
s3_bucket = s3.Bucket(
    "s3-bucket",
    acl="private",
    bucket=f"{env}.{r53_root_zone_name}",
    loggings=[
        s3.BucketLoggingArgs(target_bucket=s3_log_bucket.id, target_prefix=f"{env}/")
    ],
    tags=base_tags,
)

pulumi.export("s3_bucket_name", s3_bucket.bucket)
pulumi.export("s3_bucket_arn", s3_bucket.arn)

# Create Web ACL for CloudFront distribution
web_acl = wafv2.WebAcl(
    "web-acl",
    name=f"web-acl-rate-limit-{env}-{r53_root_zone_name.replace('.', '-')}",
    description="CAPTCHA on rate limit",
    default_action=wafv2.WebAclDefaultActionArgs(
        allow={},
    ),
    rules=[
        wafv2.WebAclRuleArgs(
            name=f"rate-limit-rule-{env}-{r53_root_zone_name.replace('.', '-')}",
            priority=1,
            action=wafv2.WebAclRuleActionArgs(
                captcha=wafv2.WebAclCaptchaConfigArgs(),
            ),
            statement=wafv2.WebAclRuleStatementArgs(
                rate_based_statement=wafv2.WebAclRuleStatementRateBasedStatementArgs(
                    aggregate_key_type="IP",
                    limit=500,
                ),
            ),
            visibility_config=wafv2.WebAclRuleVisibilityConfigArgs(
                cloudwatch_metrics_enabled=True,
                sampled_requests_enabled=True,
                metric_name=f"rate-limit-rule-{env}-{r53_root_zone_name.replace('.', '-')}",
            ),
        )
    ],
    visibility_config=wafv2.WebAclVisibilityConfigArgs(
        cloudwatch_metrics_enabled=True,
        sampled_requests_enabled=True,
        metric_name=f"web-acl-rate-limit-{env}-{r53_root_zone_name.replace('.', '-')}",
    ),
    scope="CLOUDFRONT",
    tags=base_tags,
)

# Create CloudFront distribution for static site
cf_origin_access_control = cloudfront.OriginAccessControl(
    "cf-origin-access-control",
    description="Origin Access Identity for S3 bucket",
    origin_access_control_origin_type="s3",
    signing_behavior="always",
    signing_protocol="sigv4",
)

cf_aliases = [f"{env}.{r53_root_zone_name}"]
if env == "prod":
    cf_aliases.append(r53_root_zone_name)

cf_default_index_function = cloudfront.Function(
    "default-index-function",
    runtime="cloudfront-js-2.0",
    publish=True,
    code=(lambda path: open(path).read())("lambda/default_index/index.js"),
)

cf_distribution = cloudfront.Distribution(
    "cf-distribution",
    enabled=True,
    aliases=cf_aliases,
    default_root_object="index.html",
    http_version="http2and3",
    is_ipv6_enabled=True,
    price_class="PriceClass_All" if env == "prod" else "PriceClass_100",
    origins=[
        cloudfront.DistributionOriginArgs(
            origin_id=s3_bucket.bucket_regional_domain_name,
            domain_name=s3_bucket.bucket_regional_domain_name,
            origin_access_control_id=cf_origin_access_control.id,
        )
    ],
    default_cache_behavior=cloudfront.DistributionDefaultCacheBehaviorArgs(
        target_origin_id=s3_bucket.bucket_regional_domain_name,
        viewer_protocol_policy="redirect-to-https",
        allowed_methods=["GET", "HEAD", "OPTIONS"],
        cached_methods=["GET", "HEAD", "OPTIONS"],
        forwarded_values=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            cookies=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="none",
            ),
            query_string=False,
        ),
        function_associations=[
            cloudfront.DistributionDefaultCacheBehaviorFunctionAssociationArgs(
                function_arn=cf_default_index_function.arn,
                event_type="viewer-request",
            ),
        ],
        min_ttl=0,
        default_ttl=3600,
        max_ttl=86400,
    ),
    viewer_certificate=cloudfront.DistributionViewerCertificateArgs(
        acm_certificate_arn=acm_cert.arn,
        ssl_support_method="sni-only",
    ),
    restrictions=cloudfront.DistributionRestrictionsArgs(
        geo_restriction=cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none",
        ),
    ),
    logging_config=cloudfront.DistributionLoggingConfigArgs(
        bucket=cf_log_bucket.bucket_regional_domain_name,
        include_cookies=False,
        prefix=f"{env}/",
    ),
    web_acl_id=web_acl.arn,
    tags=base_tags,
)

cf_s3_bucket_policy = s3.BucketPolicy(
    "cf-s3-bucket-policy",
    bucket=s3_bucket.id,
    policy=pulumi.Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudfront.amazonaws.com"},
                    "Action": "s3:GetObject",
                    "Resource": [s3_bucket.arn.apply(lambda arn: f"{arn}/*")],
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceArn": cf_distribution.arn,
                        }
                    },
                }
            ],
        }
    ),
)

pulumi.export("cf_distribution_id", cf_distribution.id)
pulumi.export("cf_distribution_domain_name", cf_distribution.domain_name)
pulumi.export("cf_distribution_arn", cf_distribution.arn)

# TODO: Remove Temp hack to keep service available in dev
if env == "dev":
    r53_root_target = config.require("r53_root_target")
    r53_env_record = route53.Record(
        "temp-record",
        name="",
        zone_id=r53_env_zone.zone_id,
        type="A",
        ttl=30,
        records=[r53_root_target],
    )
else:
    r53_env_record = route53.Record(
        "env-record",
        name="",
        zone_id=r53_env_zone.zone_id,
        type="A",
        aliases=[
            route53.RecordAliasArgs(
                name=cf_distribution.domain_name,
                zone_id=cf_distribution.hosted_zone_id,
                evaluate_target_health=False,
            )
        ],
    )

    # In Prod we create a root record for the root domain
    if env == "prod":
        r53_root_record = route53.Record(
            "root-record",
            name="",
            zone_id=r53_root_zone.zone_id,
            type="A",
            aliases=[
                route53.RecordAliasArgs(
                    name=cf_distribution.domain_name,
                    zone_id=cf_distribution.hosted_zone_id,
                    evaluate_target_health=False,
                )
            ],
        )
