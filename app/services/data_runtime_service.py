"""数据能力运行时查询层"""


SAMPLE_DATASETS = {
    "fact_daily_metric": {
        "headline": "经营指标日表",
        "observations": [
            "近 7 日收入同比 +8.4%，但华东区回款速度较上周放缓 2 天。",
            "人效指标整体平稳，售后工单处理时长较目标多 11%。",
        ],
    },
    "fact_project_budget": {
        "headline": "项目预算事实表",
        "observations": [
            "核心项目本月预算执行率 112%，主要超支集中在外采服务和差旅。",
            "两项延期项目的预算偏差已连续两个月扩大，需要复核范围蔓延原因。",
        ],
    },
    "fact_approval_log": {
        "headline": "审批日志明细",
        "observations": [
            "平均审批时长 2.3 天，法务节点是当前最主要瓶颈。",
            "跨部门会签单据在周三集中积压，导致立项周期延长。",
        ],
    },
}


class DataRuntimeService:
    def query(self, assets: list, query: str) -> list[dict]:
        summaries = []
        for asset in assets:
            if asset.status != "active":
                continue
            dataset = SAMPLE_DATASETS.get(asset.table_name)
            if not dataset:
                summaries.append(
                    {
                        "asset_id": asset.id,
                        "display_name": asset.display_name,
                        "summary": asset.scope_summary,
                        "observations": [f"已授权读取 {asset.display_name}，当前未配置示例数据。"],
                    }
                )
                continue

            observations = list(dataset["observations"])
            lowered = query.lower()
            if "预算" in query and asset.table_name != "fact_project_budget":
                observations = observations[:1]
            if "审批" in query and asset.table_name != "fact_approval_log":
                observations = observations[:1]
            if any(keyword in lowered for keyword in ["收入", "经营", "复盘", "指标"]) and asset.table_name != "fact_daily_metric":
                observations = observations[:1]
            summaries.append(
                {
                    "asset_id": asset.id,
                    "display_name": asset.display_name,
                    "summary": asset.scope_summary,
                    "observations": observations,
                }
            )
        return summaries


data_runtime_service = DataRuntimeService()
