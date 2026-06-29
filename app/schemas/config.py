"""业务域和企业实际角色的 Pydantic schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BusinessDomainBase(BaseModel):
    name: str = Field(..., max_length=200)
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class BusinessDomainCreate(BusinessDomainBase):
    pass


class BusinessDomainUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class BusinessDomainOut(BusinessDomainBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EnterpriseRoleBase(BaseModel):
    business_domain_id: str
    name: str = Field(..., max_length=200)
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class EnterpriseRoleCreate(EnterpriseRoleBase):
    pass


class EnterpriseRoleUpdate(BaseModel):
    business_domain_id: Optional[str] = None
    name: Optional[str] = Field(None, max_length=200)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class EnterpriseRoleOut(EnterpriseRoleBase):
    id: str
    business_domain_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
