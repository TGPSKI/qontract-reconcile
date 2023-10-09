"""
Generated by qenerate plugin=pydantic_v1. DO NOT MODIFY MANUALLY!
"""
from collections.abc import Callable  # noqa: F401 # pylint: disable=W0611
from datetime import datetime  # noqa: F401 # pylint: disable=W0611
from enum import Enum  # noqa: F401 # pylint: disable=W0611
from typing import (  # noqa: F401 # pylint: disable=W0611
    Any,
    Optional,
    Union,
)

from pydantic import (  # noqa: F401 # pylint: disable=W0611
    BaseModel,
    Extra,
    Field,
    Json,
)

from reconcile.gql_definitions.fragments.jumphost_common_fields import (
    CommonJumphostFields,
)
from reconcile.gql_definitions.fragments.deplopy_resources import DeployResourcesFields
from reconcile.gql_definitions.fragments.minimal_ocm_organization import (
    MinimalOCMOrganization,
)
from reconcile.gql_definitions.fragments.vault_secret import VaultSecret


DEFINITION = """
fragment CommonJumphostFields on ClusterJumpHost_v1 {
  hostname
  knownHosts
  user
  port
  remotePort
  identity {
    ... VaultSecret
  }
}

fragment DeployResourcesFields on DeployResources_v1 {
  requests {
    cpu
    memory
  }
  limits {
    cpu
    memory
  }
}

fragment MinimalOCMOrganization on OpenShiftClusterManager_v1 {
  name
  orgId
}

fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}

query Integrations {
  integrations: integrations_v1 {
    name
    upstream
    managed {
      namespace {
        path
        name
        environment {
          name
          parameters
        }
        cluster {
          name
          serverUrl
          insecureSkipTLSVerify
          jumpHost {
            ...CommonJumphostFields
          }
          automationToken {
            ... VaultSecret
          }
        }
      }
      spec {
        cache
        command
        disableUnleash
        environmentAware
        extraArgs
        extraEnv {
          secretName
          secretKey
          name
          value
        }
        internalCertificates
        logs {
          slack
          googleChat
        }
        resources {
          ... DeployResourcesFields
        }
        fluentdResources {
          ... DeployResourcesFields
        }
        sleepDurationSecs
        state
        storage
        trigger
        cron
        dashdotdb
        concurrencyPolicy
        restartPolicy
        successfulJobHistoryLimit
        failedJobHistoryLimit
        imageRef
        enablePushgateway
      }
      sharding {
        strategy

        ... on StaticSharding_v1 {
          shards
        }

        ... on OpenshiftClusterSharding_v1 {
            shardSpecOverrides {
              shard {
                  name
              }
              imageRef
              disabled
              resources {
                ... DeployResourcesFields
              }
              subSharding {
                strategy
                ... on StaticSubSharding_v1 {
                  shards
                }
              }
            }
        }


        ... on OCMOrganizationSharding_v1 {
            shardSpecOverrides {
              shard {
                  ... MinimalOCMOrganization
              }
              imageRef
              disabled
              resources {
                ... DeployResourcesFields
              }
            }
        }


        ... on AWSAccountSharding_v1 {
            shardSpecOverrides {
              shard {
                name
                disable {
                  integrations
                }
              }
              imageRef
              disabled
              resources {
                ... DeployResourcesFields
              }
            }
        }


        ... on CloudflareDNSZoneSharding_v1 {
          shardSpecOverrides {
            shard {
              zone
              identifier
            }
            imageRef
            disabled
            resources {
              ... DeployResourcesFields
            }
          }
        }
      }
    }
  }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union = True
        extra = Extra.forbid


class EnvironmentV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    parameters: Optional[Json] = Field(..., alias="parameters")


class ClusterV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    server_url: str = Field(..., alias="serverUrl")
    insecure_skip_tls_verify: Optional[bool] = Field(..., alias="insecureSkipTLSVerify")
    jump_host: Optional[CommonJumphostFields] = Field(..., alias="jumpHost")
    automation_token: Optional[VaultSecret] = Field(..., alias="automationToken")


class NamespaceV1(ConfiguredBaseModel):
    path: str = Field(..., alias="path")
    name: str = Field(..., alias="name")
    environment: EnvironmentV1 = Field(..., alias="environment")
    cluster: ClusterV1 = Field(..., alias="cluster")


class IntegrationSpecExtraEnvV1(ConfiguredBaseModel):
    secret_name: Optional[str] = Field(..., alias="secretName")
    secret_key: Optional[str] = Field(..., alias="secretKey")
    name: Optional[str] = Field(..., alias="name")
    value: Optional[str] = Field(..., alias="value")


class IntegrationSpecLogsV1(ConfiguredBaseModel):
    slack: Optional[bool] = Field(..., alias="slack")
    google_chat: Optional[bool] = Field(..., alias="googleChat")


class IntegrationSpecV1(ConfiguredBaseModel):
    cache: Optional[bool] = Field(..., alias="cache")
    command: Optional[str] = Field(..., alias="command")
    disable_unleash: Optional[bool] = Field(..., alias="disableUnleash")
    environment_aware: Optional[bool] = Field(..., alias="environmentAware")
    extra_args: Optional[str] = Field(..., alias="extraArgs")
    extra_env: Optional[list[IntegrationSpecExtraEnvV1]] = Field(..., alias="extraEnv")
    internal_certificates: Optional[bool] = Field(..., alias="internalCertificates")
    logs: Optional[IntegrationSpecLogsV1] = Field(..., alias="logs")
    resources: Optional[DeployResourcesFields] = Field(..., alias="resources")
    fluentd_resources: Optional[DeployResourcesFields] = Field(
        ..., alias="fluentdResources"
    )
    sleep_duration_secs: Optional[str] = Field(..., alias="sleepDurationSecs")
    state: Optional[bool] = Field(..., alias="state")
    storage: Optional[str] = Field(..., alias="storage")
    trigger: Optional[bool] = Field(..., alias="trigger")
    cron: Optional[str] = Field(..., alias="cron")
    dashdotdb: Optional[bool] = Field(..., alias="dashdotdb")
    concurrency_policy: Optional[str] = Field(..., alias="concurrencyPolicy")
    restart_policy: Optional[str] = Field(..., alias="restartPolicy")
    successful_job_history_limit: Optional[int] = Field(
        ..., alias="successfulJobHistoryLimit"
    )
    failed_job_history_limit: Optional[int] = Field(..., alias="failedJobHistoryLimit")
    image_ref: Optional[str] = Field(..., alias="imageRef")
    enable_pushgateway: Optional[bool] = Field(..., alias="enablePushgateway")


class IntegrationShardingV1(ConfiguredBaseModel):
    strategy: str = Field(..., alias="strategy")


class StaticShardingV1(IntegrationShardingV1):
    shards: int = Field(..., alias="shards")


class OpenshiftClusterShardSpecOverrideV1_ClusterV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")


class SubShardingV1(ConfiguredBaseModel):
    strategy: str = Field(..., alias="strategy")


class StaticSubShardingV1(SubShardingV1):
    shards: int = Field(..., alias="shards")


class OpenshiftClusterShardSpecOverrideV1(ConfiguredBaseModel):
    shard: OpenshiftClusterShardSpecOverrideV1_ClusterV1 = Field(..., alias="shard")
    image_ref: Optional[str] = Field(..., alias="imageRef")
    disabled: Optional[bool] = Field(..., alias="disabled")
    resources: Optional[DeployResourcesFields] = Field(..., alias="resources")
    sub_sharding: Optional[Union[StaticSubShardingV1, SubShardingV1]] = Field(
        ..., alias="subSharding"
    )


class OpenshiftClusterShardingV1(IntegrationShardingV1):
    shard_spec_overrides: Optional[list[OpenshiftClusterShardSpecOverrideV1]] = Field(
        ..., alias="shardSpecOverrides"
    )


class OCMOrganizationShardSpecOverrideV1(ConfiguredBaseModel):
    shard: MinimalOCMOrganization = Field(..., alias="shard")
    image_ref: Optional[str] = Field(..., alias="imageRef")
    disabled: Optional[bool] = Field(..., alias="disabled")
    resources: Optional[DeployResourcesFields] = Field(..., alias="resources")


class OCMOrganizationShardingV1(IntegrationShardingV1):
    shard_spec_overrides: Optional[list[OCMOrganizationShardSpecOverrideV1]] = Field(
        ..., alias="shardSpecOverrides"
    )


class DisableClusterAutomationsV1(ConfiguredBaseModel):
    integrations: Optional[list[str]] = Field(..., alias="integrations")


class AWSAccountV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    disable: Optional[DisableClusterAutomationsV1] = Field(..., alias="disable")


class AWSAccountShardSpecOverrideV1(ConfiguredBaseModel):
    shard: AWSAccountV1 = Field(..., alias="shard")
    image_ref: Optional[str] = Field(..., alias="imageRef")
    disabled: Optional[bool] = Field(..., alias="disabled")
    resources: Optional[DeployResourcesFields] = Field(..., alias="resources")


class AWSAccountShardingV1(IntegrationShardingV1):
    shard_spec_overrides: Optional[list[AWSAccountShardSpecOverrideV1]] = Field(
        ..., alias="shardSpecOverrides"
    )


class CloudflareDnsZoneV1(ConfiguredBaseModel):
    zone: str = Field(..., alias="zone")
    identifier: str = Field(..., alias="identifier")


class CloudflareDNSZoneShardSpecOverrideV1(ConfiguredBaseModel):
    shard: CloudflareDnsZoneV1 = Field(..., alias="shard")
    image_ref: Optional[str] = Field(..., alias="imageRef")
    disabled: Optional[bool] = Field(..., alias="disabled")
    resources: Optional[DeployResourcesFields] = Field(..., alias="resources")


class CloudflareDNSZoneShardingV1(IntegrationShardingV1):
    shard_spec_overrides: Optional[list[CloudflareDNSZoneShardSpecOverrideV1]] = Field(
        ..., alias="shardSpecOverrides"
    )


class IntegrationManagedV1(ConfiguredBaseModel):
    namespace: NamespaceV1 = Field(..., alias="namespace")
    spec: IntegrationSpecV1 = Field(..., alias="spec")
    sharding: Optional[
        Union[
            StaticShardingV1,
            OpenshiftClusterShardingV1,
            OCMOrganizationShardingV1,
            AWSAccountShardingV1,
            CloudflareDNSZoneShardingV1,
            IntegrationShardingV1,
        ]
    ] = Field(..., alias="sharding")


class IntegrationV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    upstream: Optional[str] = Field(..., alias="upstream")
    managed: Optional[list[IntegrationManagedV1]] = Field(..., alias="managed")


class IntegrationsQueryData(ConfiguredBaseModel):
    integrations: Optional[list[IntegrationV1]] = Field(..., alias="integrations")


def query(query_func: Callable, **kwargs: Any) -> IntegrationsQueryData:
    """
    This is a convenience function which queries and parses the data into
    concrete types. It should be compatible with most GQL clients.
    You do not have to use it to consume the generated data classes.
    Alternatively, you can also mime and alternate the behavior
    of this function in the caller.

    Parameters:
        query_func (Callable): Function which queries your GQL Server
        kwargs: optional arguments that will be passed to the query function

    Returns:
        IntegrationsQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return IntegrationsQueryData(**raw_data)
