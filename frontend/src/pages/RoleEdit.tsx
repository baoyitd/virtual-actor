import {
  ArrowLeft,
  BookOpen,
  Check,
  ChevronDown,
  ChevronRight,
  FolderTree,
  Info,
  Save,
  Search,
  Settings2,
  ShieldAlert,
  Wand2,
  X,
} from 'lucide-react';
import { useDeferredValue, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import type { KnowledgeBaseItem, KnowledgeItem, KnowledgeRef, RoleDetail } from '../api';

const emptyForm = {
  name: '',
  bio: '',
  tags: '',
  identity_background: '',
  point_of_view: '',
  decision_style: 'balanced',
  responsibility_boundary: '',
  speaking_style: '',
  collaboration_mode: 'independent',
  capability_boundary: '',
  model_provider: 'custom',
  model_name: 'deepseek-v4-pro',
  temperature: '0.3',
  max_tokens: '4096',
};

type FormState = typeof emptyForm;

type DirectoryNode = {
  name: string;
  path: string;
  children: DirectoryNode[];
  files: KnowledgeItem[];
};

type TemplatePreset = {
  id: string;
  name: string;
  summary: string;
  tags: string;
  values: Partial<FormState>;
};

type PreviewKnowledge = {
  kb_id: string;
  knowledge_object_id: string;
  knowledge_version_id: string | null;
  title: string;
  type?: string | null;
  summary: string;
};

const roleTemplates: TemplatePreset[] = [
  {
    id: 'blank',
    name: '空白开始',
    summary: '保留默认推荐配置，从空白表单开始填写。',
    tags: '',
    values: {},
  },
  {
    id: 'operator-analysis',
    name: '经营分析顾问',
    summary: '适合经营复盘、损益分析、经营动作建议等商务场景。',
    tags: '经营, 分析, 业务',
    values: {
      name: '经营分析顾问',
      bio: '面向管理层输出经营表现解读、问题归因和后续动作建议。',
      identity_background: '具备企业经营分析、预算跟踪和经营复盘经验，能够从收入、成本、效率和组织动作多维度看问题。',
      point_of_view: '优先关注经营结果背后的关键驱动因素，强调用数据解释现象，用业务动作闭环问题。',
      decision_style: 'balanced',
      responsibility_boundary: '负责识别经营问题、拆解驱动因素并提出可执行建议；不直接代替业务负责人作最终经营决策。',
      speaking_style: '表达清晰、结构化，先给结论，再给依据与建议，尽量使用管理层能快速理解的商务语言。',
      collaboration_mode: 'consulting',
      capability_boundary: '能基于绑定知识和输入数据给出分析与建议；缺少数据或知识时必须明确说明，不虚构结论。',
    },
  },
  {
    id: 'industry-research',
    name: '行业研究顾问',
    summary: '适合市场研究、竞品分析、趋势判断和高层材料整理。',
    tags: '研究, 行业, 战略',
    values: {
      name: '行业研究顾问',
      bio: '用于输出行业格局、竞争态势和趋势判断的研究型角色。',
      identity_background: '具备行业研究、商业分析和资料整合经验，擅长从公开资料与内部材料中提炼结论。',
      point_of_view: '优先判断行业结构变化、关键变量和竞争对手动作，避免只做资料堆砌。',
      decision_style: 'balanced',
      responsibility_boundary: '负责形成研究观点、风险提示和机会判断；不直接替代投资、战略或业务负责人拍板。',
      speaking_style: '正式、克制、偏咨询风格，强调信息来源和判断依据。',
      collaboration_mode: 'consulting',
      capability_boundary: '只能基于已有资料做研究判断，不承诺外部未验证信息，也不虚构一手调研结果。',
    },
  },
  {
    id: 'risk-compliance',
    name: '风控合规审阅',
    summary: '适合制度审阅、风险排查、操作合规和边界提醒。',
    tags: '风控, 合规, 审阅',
    values: {
      name: '风控合规审阅',
      bio: '用于识别制度、流程和业务动作中的合规风险与执行缺口。',
      identity_background: '具备制度管理、内控审查和风险评估经验，熟悉企业流程控制和合规表述。',
      point_of_view: '优先识别风险暴露点、权限边界和执行漏洞，对不清晰事项保持审慎。',
      decision_style: 'conservative',
      responsibility_boundary: '负责指出风险点、提出整改建议和补充条件；不代替法务、审计或管理层作最终裁定。',
      speaking_style: '稳重、审慎、边界清晰，避免绝对化措辞。',
      collaboration_mode: 'consulting',
      capability_boundary: '能够做合规与风险提示，但不是法律意见，不对缺失资料做推断式背书。',
    },
  },
  {
    id: 'governance-assistant',
    name: '项目治理助手',
    summary: '适合跨部门协同、任务推进、里程碑和治理规则执行。',
    tags: '治理, 项目, 协同',
    values: {
      name: '项目治理助手',
      bio: '面向跨团队协作与治理场景，帮助澄清边界、推进事项和收口结论。',
      identity_background: '具备项目管理、流程治理和跨部门协同经验，关注责任归属、节奏和证据闭环。',
      point_of_view: '优先澄清责任边界、依赖关系和交付证据，避免口径漂移和重复沟通。',
      decision_style: 'balanced',
      responsibility_boundary: '负责梳理现状、收口问题和推进执行计划；不代替业务 owner 做最终业务取舍。',
      speaking_style: '简洁、正式、直接，强调状态、风险和下一步动作。',
      collaboration_mode: 'delegatable',
      capability_boundary: '能组织信息和推进收口，但不能在证据缺失时自行裁决超边界事项。',
    },
  },
];

const knowledgeSelectionNote = '当前文件级绑定用于展示、发布追溯和确定测试检索所涉及的知识库范围；本轮不承诺文件级检索约束。';

function knowledgeKey(item: { kb_id: string; knowledge_object_id: string }) {
  return `${item.kb_id}::${item.knowledge_object_id}`;
}

function buildDirectoryTree(items: KnowledgeItem[]): DirectoryNode[] {
  type MutableNode = {
    name: string;
    path: string;
    children: Map<string, MutableNode>;
    files: KnowledgeItem[];
  };

  const createNode = (name: string, path: string): MutableNode => ({
    name,
    path,
    children: new Map<string, MutableNode>(),
    files: [],
  });

  const root = createNode('', '');
  for (const item of items) {
    const parts = item.knowledge_object_id.split('/').filter(Boolean);
    const directories = parts.length > 1 ? parts.slice(0, -1) : [];
    let current = root;
    let currentPath = '';
    for (const segment of directories) {
      currentPath = currentPath ? `${currentPath}/${segment}` : segment;
      if (!current.children.has(segment)) {
        current.children.set(segment, createNode(segment, currentPath));
      }
      current = current.children.get(segment)!;
    }
    current.files.push(item);
  }

  const finalize = (node: MutableNode): DirectoryNode => ({
    name: node.name,
    path: node.path,
    files: [...node.files].sort((left, right) => left.title.localeCompare(right.title, 'zh-CN')),
    children: Array.from(node.children.values())
      .sort((left, right) => left.name.localeCompare(right.name, 'zh-CN'))
      .map(finalize),
  });

  return Array.from(root.children.values())
    .sort((left, right) => left.name.localeCompare(right.name, 'zh-CN'))
    .map(finalize);
}

function collectDirectoryItems(node: DirectoryNode): KnowledgeItem[] {
  return [
    ...node.files,
    ...node.children.flatMap(collectDirectoryItems),
  ];
}

function matchesKnowledge(item: KnowledgeItem, keyword: string) {
  const normalized = keyword.trim().toLowerCase();
  if (!normalized) return true;
  const haystack = [
    item.title,
    item.knowledge_object_id,
    item.summary,
    item.type || '',
    item.tags.join(' '),
  ].join(' ').toLowerCase();
  return haystack.includes(normalized);
}

function hasMeaningfulInput(form: FormState) {
  return (Object.keys(emptyForm) as Array<keyof FormState>).some(key => form[key] !== emptyForm[key]);
}

export function RoleEdit() {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const [form, setForm] = useState<FormState>(emptyForm);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseItem[]>([]);
  const [catalogByKb, setCatalogByKb] = useState<Record<string, KnowledgeItem[]>>({});
  const [bound, setBound] = useState<KnowledgeRef[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(Boolean(id));
  const [loadingCatalog, setLoadingCatalog] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [catalogError, setCatalogError] = useState('');
  const [catalogOpen, setCatalogOpen] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [search, setSearch] = useState('');
  const deferredSearch = useDeferredValue(search);
  const [activeTemplateId, setActiveTemplateId] = useState('blank');
  const [expandedKbIds, setExpandedKbIds] = useState<Set<string>>(new Set());
  const [expandedDirKeys, setExpandedDirKeys] = useState<Set<string>>(new Set());

  async function loadKnowledgeCatalogs(bases: KnowledgeBaseItem[]) {
    if (!bases.length) {
      setCatalogByKb({});
      return;
    }
    setLoadingCatalog(true);
    setCatalogError('');
    try {
      const entries = await Promise.all(
        bases.map(async base => [base.kb_id, await api.catalog(base.kb_id)] as const),
      );
      setCatalogByKb(Object.fromEntries(entries));
      setExpandedKbIds(prev => prev.size ? prev : new Set(bases.slice(0, 2).map(base => base.kb_id)));
    } catch (err) {
      setCatalogError(err instanceof Error ? err.message : '加载知识目录失败');
    } finally {
      setLoadingCatalog(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const [bases, role] = await Promise.all([
          api.knowledgeBases(),
          id ? api.getRole(id) : Promise.resolve(null as RoleDetail | null),
        ]);
        if (cancelled) return;

        setKnowledgeBases(bases);
        setExpandedKbIds(new Set(bases.slice(0, 2).map(base => base.kb_id)));

        if (role) {
          setForm({
            name: role.name,
            bio: role.bio,
            tags: role.tags.join(', '),
            identity_background: role.identity_background || '',
            point_of_view: role.point_of_view || '',
            decision_style: role.decision_style || 'balanced',
            responsibility_boundary: role.responsibility_boundary || '',
            speaking_style: role.speaking_style || '',
            collaboration_mode: role.collaboration_mode || 'independent',
            capability_boundary: role.capability_boundary || '',
            model_provider: role.model_binding?.model_provider || 'custom',
            model_name: role.model_binding?.model_name || 'deepseek-v4-pro',
            temperature: String(role.model_binding?.temperature ?? 0.3),
            max_tokens: String(role.model_binding?.max_tokens ?? 4096),
          });
          setBound(role.knowledge_refs);
          setSelected(new Set(role.knowledge_refs.map(ref => knowledgeKey(ref))));
          setShowAdvanced(Boolean(
            (role.model_binding?.model_provider && role.model_binding.model_provider !== emptyForm.model_provider)
            || (role.model_binding?.model_name && role.model_binding.model_name !== emptyForm.model_name)
            || String(role.model_binding?.temperature ?? emptyForm.temperature) !== emptyForm.temperature
            || String(role.model_binding?.max_tokens ?? emptyForm.max_tokens) !== emptyForm.max_tokens,
          ));
        } else {
          setActiveTemplateId('blank');
        }

        void loadKnowledgeCatalogs(bases);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : '加载编辑数据失败');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  const knowledgeBaseMap = useMemo(
    () => new Map(knowledgeBases.map(base => [base.kb_id, base.name])),
    [knowledgeBases],
  );

  const allCatalogItems = useMemo(
    () => Object.values(catalogByKb).flat(),
    [catalogByKb],
  );

  const selectedItems = useMemo(
    () => allCatalogItems.filter(item => selected.has(knowledgeKey(item))),
    [allCatalogItems, selected],
  );

  const selectedPreview = useMemo(() => {
    const previewMap = new Map<string, PreviewKnowledge>();
    for (const item of selectedItems) {
      previewMap.set(knowledgeKey(item), {
        kb_id: item.kb_id,
        knowledge_object_id: item.knowledge_object_id,
        knowledge_version_id: item.knowledge_version_id,
        title: item.title,
        type: item.type,
        summary: item.summary,
      });
    }
    for (const ref of bound) {
      const key = knowledgeKey(ref);
      if (selected.has(key) && !previewMap.has(key)) {
        previewMap.set(key, {
          kb_id: ref.kb_id,
          knowledge_object_id: ref.knowledge_object_id,
          knowledge_version_id: ref.knowledge_version_id,
          title: ref.title || ref.knowledge_object_id,
          type: ref.type,
          summary: '',
        });
      }
    }
    return Array.from(previewMap.values()).sort((left, right) => {
      if (left.kb_id !== right.kb_id) return left.kb_id.localeCompare(right.kb_id, 'zh-CN');
      return left.title.localeCompare(right.title, 'zh-CN');
    });
  }, [bound, selected, selectedItems]);

  const selectedGroups = useMemo(() => {
    const grouped = new Map<string, { kb_id: string; name: string; items: PreviewKnowledge[] }>();
    for (const item of selectedPreview) {
      if (!grouped.has(item.kb_id)) {
        grouped.set(item.kb_id, {
          kb_id: item.kb_id,
          name: knowledgeBaseMap.get(item.kb_id) || `未识别知识库 ${item.kb_id}`,
          items: [],
        });
      }
      grouped.get(item.kb_id)!.items.push(item);
    }
    return Array.from(grouped.values());
  }, [knowledgeBaseMap, selectedPreview]);

  const filteredCatalogByKb = useMemo(() => {
    const keyword = deferredSearch.trim();
    return Object.fromEntries(
      knowledgeBases.map(base => {
        const items = catalogByKb[base.kb_id] || [];
        return [
          base.kb_id,
          keyword ? items.filter(item => matchesKnowledge(item, keyword)) : items,
        ];
      }),
    ) as Record<string, KnowledgeItem[]>;
  }, [catalogByKb, deferredSearch, knowledgeBases]);

  const treeByKb = useMemo(() => Object.fromEntries(
    knowledgeBases.map(base => [base.kb_id, buildDirectoryTree(filteredCatalogByKb[base.kb_id] || [])]),
  ) as Record<string, DirectoryNode[]>, [filteredCatalogByKb, knowledgeBases]);

  const update = (key: keyof FormState, value: string) => setForm(prev => ({ ...prev, [key]: value }));

  const toggleSelection = (item: { kb_id: string; knowledge_object_id: string }) => {
    const key = knowledgeKey(item);
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const toggleDirectory = (items: KnowledgeItem[], shouldSelect: boolean) => {
    setSelected(prev => {
      const next = new Set(prev);
      for (const item of items) {
        const key = knowledgeKey(item);
        if (shouldSelect) next.add(key);
        else next.delete(key);
      }
      return next;
    });
  };

  const toggleKbExpanded = (kbId: string) => {
    setExpandedKbIds(prev => {
      const next = new Set(prev);
      if (next.has(kbId)) next.delete(kbId);
      else next.add(kbId);
      return next;
    });
  };

  const toggleDirectoryExpanded = (kbId: string, path: string) => {
    const key = `${kbId}:${path}`;
    setExpandedDirKeys(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const applyTemplate = (templateId: string) => {
    const template = roleTemplates.find(item => item.id === templateId);
    if (!template) return;

    if ((hasMeaningfulInput(form) || selected.size > 0) && templateId !== activeTemplateId) {
      const confirmed = window.confirm('套用模板会覆盖当前已填写的角色字段示例，是否继续？');
      if (!confirmed) return;
    }

    setForm(prev => ({
      ...emptyForm,
      model_provider: prev.model_provider,
      model_name: prev.model_name,
      temperature: prev.temperature,
      max_tokens: prev.max_tokens,
      ...template.values,
      tags: template.tags,
    }));
    setActiveTemplateId(template.id);
  };

  const save = async () => {
    if (!form.name.trim() || !form.bio.trim()) {
      setError('角色名称和一句话简介不能为空');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const payload = {
        name: form.name.trim(),
        bio: form.bio.trim(),
        tags: form.tags.split(',').map(tag => tag.trim()).filter(Boolean),
        identity_background: form.identity_background.trim(),
        point_of_view: form.point_of_view.trim(),
        decision_style: form.decision_style,
        responsibility_boundary: form.responsibility_boundary.trim(),
        speaking_style: form.speaking_style.trim(),
        collaboration_mode: form.collaboration_mode,
        capability_boundary: form.capability_boundary.trim(),
        model_binding: {
          model_provider: form.model_provider.trim(),
          model_name: form.model_name.trim(),
          temperature: Number(form.temperature),
          max_tokens: Number(form.max_tokens),
        },
      };
      const role = id ? await api.updateRole(id, payload) : await api.createRole(payload);
      const roleId = role.role_id;
      const boundByKey = new Map(bound.map(ref => [knowledgeKey(ref), ref]));

      for (const ref of bound) {
        if (!selected.has(knowledgeKey(ref))) {
          await api.unbindKnowledge(roleId, ref.id);
        }
      }

      for (const item of selectedItems) {
        const key = knowledgeKey(item);
        if (!boundByKey.has(key)) {
          await api.bindKnowledge(roleId, {
            kb_id: item.kb_id,
            knowledge_object_id: item.knowledge_object_id,
            knowledge_version_id: item.knowledge_version_id,
            title: item.title,
            type: item.type,
          });
        }
      }

      nav(`/roles/${roleId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const renderDirectoryNode = (kbId: string, node: DirectoryNode, depth = 0) => {
    const allItems = collectDirectoryItems(node);
    const selectedCount = allItems.filter(item => selected.has(knowledgeKey(item))).length;
    const fullySelected = allItems.length > 0 && selectedCount === allItems.length;
    const partiallySelected = selectedCount > 0 && selectedCount < allItems.length;
    const expanded = deferredSearch.trim() ? true : expandedDirKeys.has(`${kbId}:${node.path}`);

    return (
      <div key={`${kbId}:${node.path}`} className="knowledge-tree-node">
        <div
          className={`directory-row${fullySelected ? ' selected' : ''}${partiallySelected ? ' partial' : ''}`}
          style={{ paddingLeft: `${12 + depth * 18}px` }}
        >
          <button
            type="button"
            className="tree-toggle-btn"
            onClick={() => toggleDirectoryExpanded(kbId, node.path)}
            aria-label={expanded ? '收起目录' : '展开目录'}
          >
            {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </button>
          <div className="directory-copy">
            <strong><FolderTree size={15} />{node.name}</strong>
            <span>当前目录共 {allItems.length} 条，可一键勾选为当前文件快照。</span>
          </div>
          <span className="directory-meta">{selectedCount}/{allItems.length}</span>
          <button
            type="button"
            className="secondary-btn small-btn"
            onClick={() => toggleDirectory(allItems, !fullySelected)}
          >
            {fullySelected ? '取消目录' : '选择目录'}
          </button>
        </div>
        {expanded && (
          <div className="directory-branch">
            {node.children.map(child => renderDirectoryNode(kbId, child, depth + 1))}
            {node.files.map(item => {
              const active = selected.has(knowledgeKey(item));
              return (
                <button
                  type="button"
                  key={knowledgeKey(item)}
                  className={`file-row${active ? ' selected' : ''}`}
                  onClick={() => toggleSelection(item)}
                  style={{ paddingLeft: `${48 + depth * 18}px` }}
                >
                  <span className="file-check">{active ? <Check size={14} /> : null}</span>
                  <div className="file-copy">
                    <strong>{item.title}</strong>
                    <small>{item.type || 'knowledge'} · {item.knowledge_version_id || '未标记版本'}</small>
                    <em>{item.summary || item.knowledge_object_id}</em>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div className="page-loading">正在加载角色配置...</div>;

  return (
    <section className="page">
      <div className="page-head compact">
        <div>
          <Link to={id ? `/roles/${id}` : '/'} className="back-link"><ArrowLeft size={16} />返回</Link>
          <h1>{id ? '编辑角色' : '新建角色'}</h1>
          <p className="subtle">按身份、判断方式、知识、能力和模型配置形成可发布角色。字段都带有中文说明和示例，可直接按模板起步。</p>
        </div>
        <button type="button" className="primary-btn" onClick={save} disabled={saving}><Save size={17} />{saving ? '保存中...' : '保存角色'}</button>
      </div>
      {error && <div className="alert error"><ShieldAlert size={17} />{error}</div>}

      <div className="form-grid role-editor-grid">
        <section className="form-section span-2">
          <div className="section-title-row">
            <h2><Wand2 size={18} />角色模板</h2>
            <span className="helper-badge">先选模板，再按业务实际微调</span>
          </div>
          <p className="subtle">模板会帮你快速写出符合中国企业语境的角色初稿。本轮模板只辅助填写，不会替你绑定具体知识。</p>
          <div className="template-library">
            {roleTemplates.map(template => (
              <button
                type="button"
                key={template.id}
                className={`template-card${activeTemplateId === template.id ? ' active' : ''}`}
                onClick={() => applyTemplate(template.id)}
              >
                <strong>{template.name}</strong>
                <p>{template.summary}</p>
                <span>{template.tags || '保留空白，按需填写'}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="form-section">
          <h2>L1 · 身份定位</h2>
          <p className="section-intro">先定义“这是谁、解决什么问题”。这部分会直接影响最终用户对角色的第一印象。</p>
          <label className="field-block">
            <span className="field-label">角色名称</span>
            <span className="field-note">给最终用户看的岗位/角色名，不写内部代号。</span>
            <input value={form.name} onChange={e => update('name', e.target.value)} placeholder="例如：经营分析顾问" />
            <span className="field-example">示例：经营分析顾问、风控合规审阅、项目治理助手</span>
          </label>
          <label className="field-block">
            <span className="field-label">一句话简介</span>
            <span className="field-note">用 20-40 字说明这个角色主要解决什么问题。</span>
            <textarea value={form.bio} onChange={e => update('bio', e.target.value)} rows={3} placeholder="例如：用于输出经营复盘、问题归因和后续动作建议。" />
            <span className="field-example">推荐写法：面向谁 + 做什么 + 输出什么。</span>
          </label>
          <label className="field-block">
            <span className="field-label">标签</span>
            <span className="field-note">方便后续筛选和识别，用中文业务词即可。</span>
            <input value={form.tags} onChange={e => update('tags', e.target.value)} placeholder="例如：经营, 分析, 治理" />
            <span className="field-example">多个标签用逗号分隔。</span>
          </label>
        </section>

        <section className="form-section">
          <h2>L2 · 判断方式</h2>
          <p className="section-intro">这部分决定角色“怎么看问题、按什么原则给建议”。</p>
          <label className="field-block">
            <span className="field-label">身份背景</span>
            <span className="field-note">写清角色基于什么经验和身份发言。</span>
            <textarea value={form.identity_background} onChange={e => update('identity_background', e.target.value)} rows={3} placeholder="例如：具备经营分析、预算跟踪和业务复盘经验。" />
            <span className="field-example">推荐写法：经验领域 + 擅长能力 + 观察视角。</span>
          </label>
          <label className="field-block">
            <span className="field-label">核心立场</span>
            <span className="field-note">说明分析问题时优先遵守的原则和偏好。</span>
            <textarea value={form.point_of_view} onChange={e => update('point_of_view', e.target.value)} rows={3} placeholder="例如：优先关注经营结果背后的关键驱动因素，不做表面结论。" />
            <span className="field-example">示例：优先风险控制、优先经营结果、优先事实依据。</span>
          </label>
          <label className="field-block">
            <span className="field-label">决策风格</span>
            <span className="field-note">控制角色建议是更保守还是更积极。</span>
            <select value={form.decision_style} onChange={e => update('decision_style', e.target.value)}>
              <option value="conservative">稳健保守</option>
              <option value="balanced">均衡审慎</option>
              <option value="aggressive">积极进取</option>
            </select>
            <span className="field-example">普通商务场景建议先用“均衡审慎”。</span>
          </label>
          <label className="field-block">
            <span className="field-label">职责边界</span>
            <span className="field-note">说明角色负责什么、不负责什么，避免用户误用。</span>
            <textarea value={form.responsibility_boundary} onChange={e => update('responsibility_boundary', e.target.value)} rows={3} placeholder="例如：负责发现问题与提出建议，不代替负责人作最终决策。" />
            <span className="field-example">推荐写法：负责事项 + 不负责事项 + 必要升级条件。</span>
          </label>
          <label className="field-block">
            <span className="field-label">表达风格</span>
            <span className="field-note">规定回答的口吻、结构和呈现方式。</span>
            <textarea value={form.speaking_style} onChange={e => update('speaking_style', e.target.value)} rows={3} placeholder="例如：先给结论，再给依据与建议，语言正式简洁。" />
            <span className="field-example">推荐写法：先结论后依据 / 结构化条列 / 商务正式语言。</span>
          </label>
        </section>

        <section className="form-section">
          <h2>L4 · 能力边界</h2>
          <p className="section-intro">告诉最终用户这个角色能协作到什么程度，以及哪些事情不能承诺。</p>
          <label className="field-block">
            <span className="field-label">协作模式</span>
            <span className="field-note">决定这个角色更像独立分析员、可委派助手还是咨询顾问。</span>
            <select value={form.collaboration_mode} onChange={e => update('collaboration_mode', e.target.value)}>
              <option value="independent">独立分析</option>
              <option value="delegatable">可委派任务</option>
              <option value="consulting">仅提供咨询</option>
            </select>
            <span className="field-example">多数商业试用角色建议选“仅提供咨询”或“独立分析”。</span>
          </label>
          <label className="field-block">
            <span className="field-label">能力边界</span>
            <span className="field-note">明确“能做什么、不能做什么、缺信息时怎么说”。</span>
            <textarea value={form.capability_boundary} onChange={e => update('capability_boundary', e.target.value)} rows={4} placeholder="例如：可基于绑定知识给出分析建议；信息不足时必须明确说明，不虚构结论。" />
            <span className="field-example">推荐写法：可执行能力 + 限制条件 + 诚实声明。</span>
          </label>
        </section>

        <section className="form-section">
          <div className="section-title-row">
            <h2><Settings2 size={18} />L5 · 高级配置</h2>
            <button type="button" className="text-toggle-btn" onClick={() => setShowAdvanced(prev => !prev)}>
              {showAdvanced ? '收起' : '展开'}
            </button>
          </div>
          <p className="section-intro">普通用户一般保持默认。只有你确实需要改变输出长度或风格时再展开修改。</p>
          {showAdvanced ? (
            <div className="two-col">
              <label className="field-block">
                <span className="field-label">模型供应方</span>
                <span className="field-note">通常按部署默认值保留即可。</span>
                <input value={form.model_provider} onChange={e => update('model_provider', e.target.value)} />
              </label>
              <label className="field-block">
                <span className="field-label">模型名称</span>
                <span className="field-note">与当前接入的模型服务保持一致。</span>
                <input value={form.model_name} onChange={e => update('model_name', e.target.value)} />
              </label>
              <label className="field-block">
                <span className="field-label">温度</span>
                <span className="field-note">越低越稳，越高越发散。商务场景建议 0.2 - 0.5。</span>
                <input type="number" step="0.1" value={form.temperature} onChange={e => update('temperature', e.target.value)} />
              </label>
              <label className="field-block">
                <span className="field-label">最大 Tokens</span>
                <span className="field-note">控制单次回复最长输出，值越大越能写全。</span>
                <input type="number" value={form.max_tokens} onChange={e => update('max_tokens', e.target.value)} />
              </label>
            </div>
          ) : (
            <div className="collapsed-note">
              <Info size={16} />
              <span>当前使用推荐默认值：`{form.model_name}` / 温度 `{form.temperature}` / 最大输出 `{form.max_tokens}`。</span>
            </div>
          )}
        </section>

        <section className="form-section span-2 knowledge-summary-section">
          <div className="section-title-row">
            <h2><BookOpen size={18} />L3 · 知识绑定</h2>
            <div className="button-row">
              <button type="button" className="secondary-btn" onClick={() => setCatalogOpen(true)}>
                <FolderTree size={16} />选择知识
              </button>
              {selected.size > 0 && (
                <button type="button" className="secondary-btn" onClick={() => setSelected(new Set())}>
                  <X size={16} />清空选择
                </button>
              )}
            </div>
          </div>
          <p className="subtle">{knowledgeSelectionNote}</p>
          {catalogError && <div className="form-error">{catalogError}</div>}
          <div className="knowledge-stats">
            <div>
              <strong>{selected.size}</strong>
              <span>已选文件</span>
            </div>
            <div>
              <strong>{new Set(selectedPreview.map(item => item.kb_id)).size}</strong>
              <span>涉及知识库</span>
            </div>
            <div>
              <strong>{allCatalogItems.length}</strong>
              <span>当前可浏览知识</span>
            </div>
          </div>
          {loadingCatalog ? (
            <div className="knowledge-empty-state">正在加载可绑定知识目录...</div>
          ) : selectedGroups.length === 0 ? (
            <div className="knowledge-empty-state">暂未绑定知识。建议先按模板完成角色定位，再打开“选择知识”按目录批量勾选。</div>
          ) : (
            <div className="selected-knowledge-groups">
              {selectedGroups.map(group => (
                <section key={group.kb_id} className="selected-knowledge-card">
                  <header>
                    <strong>{group.name}</strong>
                    <span>{group.items.length} 条已选</span>
                  </header>
                  <div className="selected-knowledge-list">
                    {group.items.slice(0, 6).map(item => (
                      <div key={`${group.kb_id}:${item.knowledge_object_id}`}>
                        <strong>{item.title}</strong>
                        <small>{item.type || 'knowledge'} · {item.knowledge_version_id || '未标记版本'}</small>
                        <span>{item.summary || item.knowledge_object_id}</span>
                      </div>
                    ))}
                    {group.items.length > 6 && <p>另有 {group.items.length - 6} 条，已在知识目录中保持选中。</p>}
                  </div>
                </section>
              ))}
            </div>
          )}
        </section>
      </div>

      {catalogOpen && (
        <div className="modal-backdrop" onClick={() => setCatalogOpen(false)}>
          <section className="knowledge-modal" onClick={event => event.stopPropagation()}>
            <header className="knowledge-modal-header">
              <div>
                <h2><FolderTree size={18} />选择知识</h2>
                <p className="subtle">支持跨多个知识库浏览，按目录批量勾选当前文件快照，再按需取消个别文件。</p>
              </div>
              <button type="button" className="secondary-btn" onClick={() => setCatalogOpen(false)}>
                <X size={16} />关闭
              </button>
            </header>

            <div className="knowledge-modal-toolbar">
              <label className="search-box knowledge-search-box">
                <Search size={16} />
                <input value={search} onChange={e => setSearch(e.target.value)} placeholder="搜索标题、路径、摘要或标签" />
              </label>
              <div className="knowledge-toolbar-meta">
                <span>已选 {selected.size} 条</span>
                <span>知识库 {knowledgeBases.length} 个</span>
              </div>
            </div>

            <div className="knowledge-browser-note">
              <Info size={16} />
              <span>{knowledgeSelectionNote}</span>
            </div>

            <div className="knowledge-browser">
              {loadingCatalog ? (
                <div className="knowledge-empty-state">正在加载知识目录...</div>
              ) : knowledgeBases.length === 0 ? (
                <div className="knowledge-empty-state">当前账号下没有可用知识库。</div>
              ) : (
                knowledgeBases.map(base => {
                  const visibleItems = filteredCatalogByKb[base.kb_id] || [];
                  const trees = treeByKb[base.kb_id] || [];
                  const selectedCount = selectedPreview.filter(item => item.kb_id === base.kb_id).length;
                  const expanded = deferredSearch.trim() ? true : expandedKbIds.has(base.kb_id);

                  if (deferredSearch.trim() && visibleItems.length === 0) {
                    return null;
                  }

                  return (
                    <section key={base.kb_id} className="knowledge-base-panel">
                      <header className="knowledge-base-header">
                        <button type="button" className="knowledge-base-toggle" onClick={() => toggleKbExpanded(base.kb_id)}>
                          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                          <strong>{base.name}</strong>
                        </button>
                        <div className="knowledge-base-meta">
                          <span>可见 {visibleItems.length} / 总计 {catalogByKb[base.kb_id]?.length || 0}</span>
                          <span>已选 {selectedCount}</span>
                        </div>
                      </header>
                      {expanded && (
                        <div className="knowledge-base-body">
                          {trees.length === 0 ? (
                            <div className="knowledge-empty-inline">当前筛选条件下没有匹配结果。</div>
                          ) : (
                            trees.map(node => renderDirectoryNode(base.kb_id, node))
                          )}
                        </div>
                      )}
                    </section>
                  );
                })
              )}
            </div>

            <footer className="knowledge-modal-footer">
              <span>已选择 {selected.size} 条知识，可直接关闭弹层继续填写角色。</span>
              <button type="button" className="primary-btn" onClick={() => setCatalogOpen(false)}>
                完成选择
              </button>
            </footer>
          </section>
        </div>
      )}
    </section>
  );
}
