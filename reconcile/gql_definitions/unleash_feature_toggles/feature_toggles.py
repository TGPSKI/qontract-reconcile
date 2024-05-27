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

from reconcile.gql_definitions.fragments.vault_secret import VaultSecret


DEFINITION = """
fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}

query UnleashFeatureToggles {
  instances: unleash_instances_v1 {
    name
    description
    url
    adminToken {
      ...VaultSecret
    }
    allowUnmanagedFeatureToggles
    projects {
      name
      feature_toggles {
        name
        description
        delete
        provider
        unleash {
          type
          impressionData
          environments
        }
      }
    }
  }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union=True
        extra=Extra.forbid


class UnleashFeatureToggleV1(ConfiguredBaseModel):
    q_type: Optional[str] = Field(..., alias="type")
    impression_data: Optional[bool] = Field(..., alias="impressionData")
    environments: Optional[Json] = Field(..., alias="environments")


class FeatureToggleUnleashV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    description: str = Field(..., alias="description")
    delete: Optional[bool] = Field(..., alias="delete")
    provider: str = Field(..., alias="provider")
    unleash: UnleashFeatureToggleV1 = Field(..., alias="unleash")


class UnleashProjectV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    feature_toggles: Optional[list[FeatureToggleUnleashV1]] = Field(..., alias="feature_toggles")


class UnleashInstanceV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    description: str = Field(..., alias="description")
    url: str = Field(..., alias="url")
    admin_token: Optional[VaultSecret] = Field(..., alias="adminToken")
    allow_unmanaged_feature_toggles: Optional[bool] = Field(..., alias="allowUnmanagedFeatureToggles")
    projects: Optional[list[UnleashProjectV1]] = Field(..., alias="projects")


class UnleashFeatureTogglesQueryData(ConfiguredBaseModel):
    instances: Optional[list[UnleashInstanceV1]] = Field(..., alias="instances")


def query(query_func: Callable, **kwargs: Any) -> UnleashFeatureTogglesQueryData:
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
        UnleashFeatureTogglesQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return UnleashFeatureTogglesQueryData(**raw_data)
