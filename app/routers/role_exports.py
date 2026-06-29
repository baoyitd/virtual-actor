"""角色外供与追溯路由"""
import io
import urllib.parse
import zipfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.schemas.export_package import ExportPackageOut, ExportPackageType
from app.services.export_service import ExportService
from app.services.role_service import RoleService

router = APIRouter(prefix="/role-assets", tags=["外供与追溯"], dependencies=[Depends(get_current_user)])


@router.get("/{role_id}/export-packages", response_model=list[ExportPackageOut])
async def list_export_packages(role_id: str, db: AsyncSession = Depends(get_db)):
    role_svc = RoleService(db)
    role = await role_svc.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    export_svc = ExportService(db)
    packages = await export_svc.list_for_role(role_id)
    results = []
    for item in packages:
        current_hash = await role_svc.get_briefing_source_hash_for_version(role_id, item.role_version_id)
        results.append(export_svc.to_schema(item, current_hash))
    return results


@router.post("/{role_id}/export-packages/{package_type}", response_model=ExportPackageOut)
async def generate_export_package(
    role_id: str,
    package_type: ExportPackageType,
    db: AsyncSession = Depends(get_db),
):
    role_svc = RoleService(db)
    role = await role_svc.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.status == "archived":
        raise HTTPException(status_code=403, detail="已归档角色不能生成新的外供")
    published_version = await role_svc.get_latest_published_version(role_id)
    if not published_version:
        raise HTTPException(status_code=400, detail="未发布角色不能生成外供")

    public_detail = await role_svc.build_version_public_detail(published_version.id)
    if not public_detail:
        raise HTTPException(status_code=404, detail="已发布版本不存在")
    if public_detail.briefing.status == "stale":
        raise HTTPException(status_code=400, detail="说明卡待确认更新，暂不能生成外供")

    current_hash = await role_svc.get_briefing_source_hash_for_version(role_id, published_version.id)
    export_svc = ExportService(db)
    record = await export_svc.generate(
        role=role,
        role_version_id=published_version.id,
        package_type=package_type,
        fields=await role_svc.get_version_fields(published_version.id),
        briefing=public_detail.briefing,
        current_source_hash=current_hash,
    )
    await db.commit()
    return export_svc.to_schema(record, current_hash)


@router.get("/{role_id}/export-packages/{package_id}/download")
async def download_export_package(
    role_id: str,
    package_id: str,
    db: AsyncSession = Depends(get_db),
):
    export_svc = ExportService(db)
    package = await export_svc.get(package_id)
    if not package or package.role_id != role_id:
        raise HTTPException(status_code=404, detail="外供包不存在")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in sorted((package.files or {}).items()):
            zf.writestr(path, content)
    buf.seek(0)

    role_svc = RoleService(db)
    role = await role_svc.get(role_id)
    role_name = role.name if role else "role"
    pkg_label = "tool" if package.package_type == "tool" else "skill"
    filename = f"{role_name}-{pkg_label}-package.zip"
    encoded_filename = urllib.parse.quote(filename)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=\"package.zip\"; filename*=UTF-8''{encoded_filename}",
        },
    )
