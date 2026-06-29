"""配置管理路由 — 业务域 + 企业实际角色"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.business_domain import BusinessDomain
from app.models.enterprise_role import EnterpriseRole
from app.models.staff_directory import StaffDirectory
from app.schemas.config import (
    BusinessDomainCreate,
    BusinessDomainOut,
    BusinessDomainUpdate,
    EnterpriseRoleCreate,
    EnterpriseRoleOut,
    EnterpriseRoleUpdate,
)

router = APIRouter(prefix="/config", tags=["配置管理"], dependencies=[Depends(get_current_user)])


# ═══ 业务域 ═══


@router.get("/business-domains", response_model=list[BusinessDomainOut])
async def list_business_domains(
    active_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BusinessDomain).order_by(BusinessDomain.sort_order, BusinessDomain.name)
    if active_only:
        stmt = stmt.where(BusinessDomain.is_active.is_(True))
    result = await db.execute(stmt)
    return [BusinessDomainOut.model_validate(item) for item in result.scalars().all()]


@router.post("/business-domains", response_model=BusinessDomainOut, status_code=201)
async def create_business_domain(data: BusinessDomainCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(BusinessDomain).where(BusinessDomain.name == data.name)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="业务域名称已存在")
    item = BusinessDomain(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return BusinessDomainOut.model_validate(item)


@router.patch("/business-domains/{domain_id}", response_model=BusinessDomainOut)
async def update_business_domain(
    domain_id: str, data: BusinessDomainUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(BusinessDomain, domain_id)
    if not item:
        raise HTTPException(status_code=404, detail="业务域不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return BusinessDomainOut.model_validate(item)


@router.delete("/business-domains/{domain_id}")
async def delete_business_domain(domain_id: str, db: AsyncSession = Depends(get_db)):
    item = await db.get(BusinessDomain, domain_id)
    if not item:
        raise HTTPException(status_code=404, detail="业务域不存在")
    roles_count = await db.execute(
        select(EnterpriseRole).where(EnterpriseRole.business_domain_id == domain_id)
    )
    if roles_count.scalars().first():
        raise HTTPException(status_code=409, detail="该业务域下仍有企业角色，不能删除")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


# ═══ 企业实际角色 ═══


@router.get("/enterprise-roles", response_model=list[EnterpriseRoleOut])
async def list_enterprise_roles(
    business_domain_id: str | None = Query(default=None),
    active_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EnterpriseRole, BusinessDomain.name).join(
        BusinessDomain, EnterpriseRole.business_domain_id == BusinessDomain.id, isouter=True
    )
    if business_domain_id:
        stmt = stmt.where(EnterpriseRole.business_domain_id == business_domain_id)
    if active_only:
        stmt = stmt.where(EnterpriseRole.is_active.is_(True))
    stmt = stmt.order_by(EnterpriseRole.sort_order, EnterpriseRole.name)
    result = await db.execute(stmt)
    items = []
    for role, domain_name in result.all():
        out = EnterpriseRoleOut.model_validate(role)
        out.business_domain_name = domain_name
        items.append(out)
    return items


@router.post("/enterprise-roles", response_model=EnterpriseRoleOut, status_code=201)
async def create_enterprise_role(data: EnterpriseRoleCreate, db: AsyncSession = Depends(get_db)):
    domain = await db.get(BusinessDomain, data.business_domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="业务域不存在")
    item = EnterpriseRole(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    out = EnterpriseRoleOut.model_validate(item)
    out.business_domain_name = domain.name
    return out


@router.patch("/enterprise-roles/{role_id}", response_model=EnterpriseRoleOut)
async def update_enterprise_role(
    role_id: str, data: EnterpriseRoleUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(EnterpriseRole, role_id)
    if not item:
        raise HTTPException(status_code=404, detail="企业角色不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    domain = await db.get(BusinessDomain, item.business_domain_id)
    out = EnterpriseRoleOut.model_validate(item)
    out.business_domain_name = domain.name if domain else None
    return out


@router.delete("/enterprise-roles/{role_id}")
async def delete_enterprise_role(role_id: str, db: AsyncSession = Depends(get_db)):
    item = await db.get(EnterpriseRole, role_id)
    if not item:
        raise HTTPException(status_code=404, detail="企业角色不存在")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


# ═══ 人员目录 ═══

INITIAL_STAFF = [
    ("张明远", "战略管理部", "zhangmy@example.com"),
    ("李静雯", "销售管理部", "lijw@example.com"),
    ("王建国", "销售管理部", "wangjg@example.com"),
    ("陈晓峰", "经营分析部", "chenxf@example.com"),
    ("刘思雨", "财务管理部", "liusy@example.com"),
    ("赵海涛", "供应链管理部", "zhaht@example.com"),
    ("孙伟杰", "营销管理部", "sunwj@example.com"),
    ("周敏华", "法务合规部", "zhoumh@example.com"),
    ("吴志强", "数字化转型部", "wuzq@example.com"),
    ("郑雅芳", "人力资源管理部", "zhengyf@example.com"),
]


@router.get("/staff", response_model=list[dict])
async def list_staff(
    active_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(StaffDirectory).order_by(StaffDirectory.name)
    if active_only:
        stmt = stmt.where(StaffDirectory.is_active.is_(True))
    result = await db.execute(stmt)
    return [
        {"id": item.id, "name": item.name, "department": item.department, "email": item.email}
        for item in result.scalars().all()
    ]


@router.post("/staff", response_model=dict, status_code=201)
async def create_staff(data: dict, db: AsyncSession = Depends(get_db)):
    item = StaffDirectory(
        name=data.get("name", ""),
        department=data.get("department"),
        email=data.get("email"),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "name": item.name, "department": item.department, "email": item.email}


@router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: str, db: AsyncSession = Depends(get_db)):
    item = await db.get(StaffDirectory, staff_id)
    if not item:
        raise HTTPException(status_code=404, detail="人员不存在")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


# ═══ 初始化种子数据 ═══

INITIAL_BUSINESS_DOMAINS = [
    "销售管理",
    "品类管理",
    "渠道管理",
    "营销管理",
    "供应链管理",
    "财务管理",
    "经营分析",
    "人力资源",
    "法务合规",
    "数字化转型",
    "投资决策",
    "质量管理",
]

INITIAL_ENTERPRISE_ROLES = {
    "销售管理": ["销售总监", "大区经理", "区域经理", "客户经理", "一线业务员"],
    "品类管理": ["品类经理", "商品规划师"],
    "渠道管理": ["渠道经理", "经销商管理经理"],
    "营销管理": ["营销总监", "品牌经理", "促销策划经理"],
    "供应链管理": ["供应链总监", "物流经理", "仓储经理"],
    "财务管理": ["财务总监", "经营分析经理", "预算经理"],
    "经营分析": ["经营分析经理", "数据分析经理"],
    "人力资源": ["人力资源总监", "组织发展经理"],
    "法务合规": ["法务总监", "合规审查主管"],
    "数字化转型": ["数字化转型负责人", "数据治理负责人"],
    "投资决策": ["投资委员会秘书", "投资分析经理"],
    "质量管理": ["质量管理总监", "品控经理"],
}


async def seed_config_data(db: AsyncSession):
    """初始化业务域和企业角色数据（仅在表为空时执行）"""
    existing = await db.execute(select(BusinessDomain).limit(1))
    if existing.scalars().first():
        return

    domain_map = {}
    for idx, name in enumerate(INITIAL_BUSINESS_DOMAINS):
        domain = BusinessDomain(name=name, sort_order=idx, is_active=True)
        db.add(domain)
        await db.flush()
        domain_map[name] = domain.id

    sort_counter = 0
    for domain_name, roles in INITIAL_ENTERPRISE_ROLES.items():
        domain_id = domain_map.get(domain_name)
        if not domain_id:
            continue
        for role_name in roles:
            db.add(
                EnterpriseRole(
                    business_domain_id=domain_id,
                    name=role_name,
                    sort_order=sort_counter,
                    is_active=True,
                )
            )
            sort_counter += 1

    existing_staff = await db.execute(select(StaffDirectory).limit(1))
    if not existing_staff.scalars().first():
        for name, dept, email in INITIAL_STAFF:
            db.add(StaffDirectory(name=name, department=dept, email=email, is_active=True))

    await db.commit()
