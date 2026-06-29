import { ArrowLeft, BookOpen, Check, ChevronDown, Database, Save, Search, Sparkles, Wand2, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  api,
  outputModeText,
  outputTypeText,
  type AIDraftResponse,
  type DataAssetSummary,
  type KnowledgeBaseItem,
  type KnowledgeBindingInput,
  type KnowledgeItem,
  type KnowledgeRef,
  type ModelBinding,
  type OutputMode,
  type RoleDetail,
} from '../api';
import { RoleStageNav } from '../components/RoleStageNav';

type FormState = {
  name: string;
  bio: string;
  tagsText: string;
  main_duty_cluster: string;
  point_of_view: string;
  decision_style: string;
  identity_background: string;
  speaking_style: string;
  knowledge_boundary: string;
  output_mode: OutputMode;
  output_type: string;
  output_schema_text: string;
  data_asset_binding_ids: string[];
  suggested_category: string;
  suggested_business_domain: string;
  model_binding: ModelBinding;
};

type KnowledgeSelection = KnowledgeBindingInput & {
  summary?: string;
  tags: string[];
};

type KnowledgeTreeNode = {
  name: string;
  path: string;
  directories: KnowledgeTreeNode[];
  files: KnowledgeItem[];
};

type KnowledgeTreeRoot = {
  directories: KnowledgeTreeNode[];
  files: KnowledgeItem[];
};

const DEFAULT_MODEL_BINDING: ModelBinding = {
  model_provider: '',
  model_name: '',
  temperature: 0.3,
  max_tokens: 4096,
  fallback_enabled: false,
  inherited: true,
};

function createEmptyForm(): FormState {
  return {
    name: '',
    bio: '',
    tagsText: '',
    main_duty_cluster: '',
    point_of_view: '',
    decision_style: '',
    identity_background: '',
    speaking_style: '',
    knowledge_boundary: '',
    output_mode: 'freeform',
    output_type: '',
    output_schema_text: '',
    data_asset_binding_ids: [],
    suggested_category: '自定义',
    suggested_business_domain: '',
    model_binding: { ...DEFAULT_MODEL_BINDING },
  };
}

function toJsonText(value: unknown) {
  return value ? JSON.stringify(value, null, 2) : '';
}

function parseJsonOrThrow(text: string) {
  const trimmed = text.trim();
  if (!trimmed) return null;
  return JSON.parse(trimmed);
}

function knowledgeKey(item: Pick<KnowledgeBindingInput, 'kb_id' | 'knowledge_object_id'>) {
  return `${item.kb_id || ''}::${item.knowledge_object_id}`;
}

function directoryKey(kbId: string, path: string) {
  return `${kbId}::${path}`;
}

function fallbackKnowledgeTitle(path: string) {
  const parts = path.split('/').filter(Boolean);
  return parts[parts.length - 1] || path;
}

function relativeKnowledgePath(knowledgeObjectId: string, kbName?: string) {
  if (kbName && knowledgeObjectId.startsWith(`${kbName}/`)) {
    const relative = knowledgeObjectId.slice(kbName.length + 1);
    return relative || fallbackKnowledgeTitle(knowledgeObjectId);
  }
  return knowledgeObjectId;
}

function selectionFromKnowledgeItem(item: KnowledgeItem): KnowledgeSelection {
  return {
    kb_id: item.kb_id,
    knowledge_object_id: item.knowledge_object_id,
    knowledge_version_id: item.knowledge_version_id,
    title: item.title || fallbackKnowledgeTitle(item.knowledge_object_id),
    type: item.type ?? null,
    summary: item.summary || '',
    tags: item.tags || [],
  };
}

function selectionFromKnowledgeRef(ref: KnowledgeRef): KnowledgeSelection {
  return {
    kb_id: ref.kb_id,
    knowledge_object_id: ref.knowledge_object_id,
    knowledge_version_id: ref.knowledge_version_id,
    title: ref.title || fallbackKnowledgeTitle(ref.knowledge_object_id),
    type: ref.type ?? null,
    summary: '',
    tags: [],
  };
}

function uniqueKnowledgeSelections(items: KnowledgeSelection[]) {
  const map = new Map<string, KnowledgeSelection>();
  items.forEach(item => {
    map.set(knowledgeKey(item), item);
  });
  return Array.from(map.values());
}

function matchesKnowledgeSearch(item: KnowledgeItem, keyword: string) {
  const needle = keyword.trim().toLowerCase();
  if (!needle) return true;
  return [
    item.title,
    item.knowledge_object_id,
    item.summary,
    ...(item.tags || []),
  ]
    .join(' ')
    .toLowerCase()
    .includes(needle);
}

function buildKnowledgeTree(items: KnowledgeItem[], kbName?: string): KnowledgeTreeRoot {
  type MutableNode = {
    name: string;
    path: string;
    directories: Map<string, MutableNode>;
    files: KnowledgeItem[];
  };

  const root: MutableNode = {
    name: '',
    path: '',
    directories: new Map(),
    files: [],
  };

  items.forEach(item => {
    const relativePath = relativeKnowledgePath(item.knowledge_object_id, kbName);
    const parts = relativePath.split('/').filter(Boolean);
    if (parts.length <= 1) {
      root.files.push(item);
      return;
    }

    let cursor = root;
    const pathParts: string[] = [];
    parts.slice(0, -1).forEach(part => {
      pathParts.push(part);
      if (!cursor.directories.has(part)) {
        cursor.directories.set(part, {
          name: part,
          path: pathParts.join('/'),
          directories: new Map(),
          files: [],
        });
      }
      cursor = cursor.directories.get(part)!;
    });
    cursor.files.push(item);
  });

  const sortByLocale = (left: string, right: string) => left.localeCompare(right, 'zh-Hans-CN');

  const finalize = (node: MutableNode): KnowledgeTreeNode => ({
    name: node.name,
    path: node.path,
    directories: Array.from(node.directories.values())
      .sort((a, b) => sortByLocale(a.path, b.path))
      .map(finalize),
    files: [...node.files].sort((a, b) =>
      sortByLocale(relativeKnowledgePath(a.knowledge_object_id, kbName), relativeKnowledgePath(b.knowledge_object_id, kbName)),
    ),
  });

  return {
    directories: Array.from(root.directories.values())
      .sort((a, b) => sortByLocale(a.path, b.path))
      .map(finalize),
    files: [...root.files].sort((a, b) =>
      sortByLocale(relativeKnowledgePath(a.knowledge_object_id, kbName), relativeKnowledgePath(b.knowledge_object_id, kbName)),
    ),
  };
}

function collectDirectoryFiles(node: KnowledgeTreeNode): KnowledgeItem[] {
  return [
    ...node.files,
    ...node.directories.flatMap(collectDirectoryFiles),
  ];
}

function collectDirectoryKeys(nodes: KnowledgeTreeNode[], kbId: string): string[] {
  const keys: string[] = [];
  nodes.forEach(node => {
    keys.push(directoryKey(kbId, node.path));
    keys.push(...collectDirectoryKeys(node.directories, kbId));
  });
  return keys;
}

export function RoleEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isCreate = !id;
  const [role, setRole] = useState<RoleDetail | null>(null);
  const [form, setForm] = useState<FormState>(createEmptyForm);
  const [templates, setTemplates] = useState<Record<string, { label?: string; fields?: Record<string, unknown> }>>({});
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseItem[]>([]);
  const [selectedKbId, setSelectedKbId] = useState('');
  const [knowledgeCatalogCache, setKnowledgeCatalogCache] = useState<Record<string, KnowledgeItem[]>>({});
  const [knowledgeCatalogLoading, setKnowledgeCatalogLoading] = useState(false);
  const [selectedKnowledgeBindings, setSelectedKnowledgeBindings] = useState<KnowledgeSelection[]>([]);
  const [draftKnowledgeBindings, setDraftKnowledgeBindings] = useState<KnowledgeSelection[]>([]);
  const [knowledgeModalOpen, setKnowledgeModalOpen] = useState(false);
  const [knowledgeSearch, setKnowledgeSearch] = useState('');
  const [expandedDirectoryKeys, setExpandedDirectoryKeys] = useState<Set<string>>(new Set());
  const [dataAssets, setDataAssets] = useState<DataAssetSummary[]>([]);
  const [intentText, setIntentText] = useState('');
  const [draftBriefing, setDraftBriefing] = useState<Pick<AIDraftResponse, 'applicable_scenarios' | 'usage_notes' | 'support_basis_summary'> | null>(null);
  const [draftNote, setDraftNote] = useState('');
  const [loading, setLoading] = useState(!isCreate);
  const [saving, setSaving] = useState(false);
  const [isDraftGenerating, setIsDraftGenerating] = useState(false);
  const [showL1Advanced, setShowL1Advanced] = useState(false);
  const [showL4Advanced, setShowL4Advanced] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.listOutputTemplates()
      .then(result => setTemplates(result as Record<string, { label?: string; fields?: Record<string, unknown> }>))
      .catch(() => undefined);
    api.listDataAssets('active').then(setDataAssets).catch(() => undefined);
    api.knowledgeBases()
      .then(items => {
        setKnowledgeBases(items);
        setSelectedKbId(prev => {
          if (prev && items.some(item => item.kb_id === prev)) {
            return prev;
          }
          return items[0]?.kb_id || '';
        });
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!selectedKbId || knowledgeCatalogCache[selectedKbId]) return;
    let active = true;
    setKnowledgeCatalogLoading(true);
    api.knowledgeCatalog(selectedKbId)
      .then(items => {
        if (!active) return;
        setKnowledgeCatalogCache(prev => ({ ...prev, [selectedKbId]: items }));
      })
      .catch(() => {
        if (!active) return;
        setKnowledgeCatalogCache(prev => ({ ...prev, [selectedKbId]: [] }));
      })
      .finally(() => {
        if (active) setKnowledgeCatalogLoading(false);
      });
    return () => {
      active = false;
    };
  }, [knowledgeCatalogCache, selectedKbId]);

  useEffect(() => {
    if (!isCreate) return;
    setRole(null);
    setForm(createEmptyForm());
    setSelectedKnowledgeBindings([]);
    setDraftBriefing(null);
    setDraftNote('');
    setLoading(false);
  }, [isCreate]);

  useEffect(() => {
    if (isCreate) return;
    setLoading(true);
    api.getRole(id!)
      .then(detail => {
        setRole(detail);
        setForm({
          name: detail.name,
          bio: detail.bio,
          tagsText: detail.tags.join('、'),
          main_duty_cluster: detail.main_duty_cluster || '',
          point_of_view: detail.point_of_view || '',
          decision_style: detail.decision_style || '',
          identity_background: detail.identity_background || '',
          speaking_style: detail.speaking_style || '',
          knowledge_boundary: detail.knowledge_boundary || '',
          output_mode: detail.output_mode,
          output_type: detail.output_type || '',
          output_schema_text: toJsonText(detail.output_schema),
          data_asset_binding_ids: detail.data_asset_bindings.map(item => item.id),
          suggested_category: detail.category,
          suggested_business_domain: detail.business_domain || '',
          model_binding: detail.model_binding ? { ...detail.model_binding } : { ...DEFAULT_MODEL_BINDING },
        });
        setSelectedKnowledgeBindings(detail.knowledge_refs.map(selectionFromKnowledgeRef));
      })
      .catch(err => setError(err instanceof Error ? err.message : '加载角色定义工作台失败'))
      .finally(() => setLoading(false));
  }, [id, isCreate]);

  const selectedAssets = useMemo(
    () => dataAssets.filter(asset => form.data_asset_binding_ids.includes(asset.id)),
    [dataAssets, form.data_asset_binding_ids],
  );

  const knowledgeBaseNameMap = useMemo(
    () => Object.fromEntries(knowledgeBases.map(item => [item.kb_id, item.name])),
    [knowledgeBases],
  );

  const currentKnowledgeBase = useMemo(
    () => knowledgeBases.find(item => item.kb_id === selectedKbId) || null,
    [knowledgeBases, selectedKbId],
  );

  const currentKnowledgeCatalog = selectedKbId ? (knowledgeCatalogCache[selectedKbId] || []) : [];

  const filteredKnowledgeCatalog = useMemo(
    () => currentKnowledgeCatalog.filter(item => matchesKnowledgeSearch(item, knowledgeSearch)),
    [currentKnowledgeCatalog, knowledgeSearch],
  );

  const knowledgeTree = useMemo(
    () => buildKnowledgeTree(filteredKnowledgeCatalog, currentKnowledgeBase?.name),
    [currentKnowledgeBase?.name, filteredKnowledgeCatalog],
  );

  const currentDirectoryKeys = useMemo(
    () => (selectedKbId ? collectDirectoryKeys(knowledgeTree.directories, selectedKbId) : []),
    [knowledgeTree.directories, selectedKbId],
  );

  useEffect(() => {
    if (!knowledgeModalOpen || !selectedKbId) return;
    if (currentDirectoryKeys.length === 0) return;
    setExpandedDirectoryKeys(prev => {
      const next = new Set(prev);
      currentDirectoryKeys.forEach(key => next.add(key));
      return next;
    });
  }, [currentDirectoryKeys, knowledgeModalOpen, selectedKbId]);

  const draftKnowledgeSet = useMemo(
    () => new Set(draftKnowledgeBindings.map(item => knowledgeKey(item))),
    [draftKnowledgeBindings],
  );

  const selectedKnowledgeGroups = useMemo(() => {
    const groups = new Map<string, { kbId: string; kbName: string; items: KnowledgeSelection[] }>();
    selectedKnowledgeBindings.forEach(item => {
      const kbId = item.kb_id || 'unknown';
      if (!groups.has(kbId)) {
        groups.set(kbId, {
          kbId,
          kbName: knowledgeBaseNameMap[kbId] || kbId,
          items: [],
        });
      }
      groups.get(kbId)!.items.push(item);
    });

    return Array.from(groups.values())
      .sort((a, b) => a.kbName.localeCompare(b.kbName, 'zh-Hans-CN'))
      .map(group => ({
        ...group,
        items: [...group.items].sort((a, b) =>
          (a.title || a.knowledge_object_id).localeCompare(b.title || b.knowledge_object_id, 'zh-Hans-CN'),
        ),
      }));
  }, [knowledgeBaseNameMap, selectedKnowledgeBindings]);

  const hasSelectedKnowledge = selectedKnowledgeBindings.length > 0;
  const hasAIGovernanceSuggestion = Boolean(draftNote || draftBriefing);
  const currentVisibleKnowledgeSelected = filteredKnowledgeCatalog.length > 0
    && filteredKnowledgeCatalog.every(item => draftKnowledgeSet.has(knowledgeKey(item)));
  const currentVisibleKnowledgeCount = filteredKnowledgeCatalog.length;

  const onField = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  const onModelField = <K extends keyof ModelBinding>(key: K, value: ModelBinding[K]) => {
    setForm(prev => ({
      ...prev,
      model_binding: {
        ...prev.model_binding,
        [key]: value,
      },
    }));
  };

  const applyDraft = (draft: AIDraftResponse) => {
    setForm(prev => ({
      ...prev,
      name: draft.name || prev.name,
      bio: draft.bio || prev.bio,
      tagsText: draft.tags.join('、'),
      main_duty_cluster: draft.main_duty_cluster || prev.main_duty_cluster,
      point_of_view: draft.point_of_view || prev.point_of_view,
      decision_style: draft.decision_style || prev.decision_style,
      identity_background: draft.identity_background || prev.identity_background,
      speaking_style: draft.speaking_style || prev.speaking_style,
      knowledge_boundary: draft.knowledge_boundary || prev.knowledge_boundary,
      output_mode: draft.output_mode,
      output_type: draft.output_type || '',
      output_schema_text: toJsonText(draft.output_schema),
      suggested_category: draft.category || prev.suggested_category,
      suggested_business_domain: draft.business_domain || prev.suggested_business_domain,
    }));
    setDraftBriefing({
      applicable_scenarios: draft.applicable_scenarios,
      usage_notes: draft.usage_notes,
      support_basis_summary: draft.support_basis_summary,
    });
    setDraftNote(draft.ai_generation_note || 'AI 草案已填入当前工作区，请继续人工确认。');
  };

  const generateDraft = async () => {
    if (!intentText.trim() || isDraftGenerating) return;
    setError('');
    setIsDraftGenerating(true);
    try {
      const draft = await api.aiDraft(intentText.trim());
      applyDraft(draft);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'AI 起草失败');
    } finally {
      setIsDraftGenerating(false);
    }
  };

  const openKnowledgeModal = () => {
    setDraftKnowledgeBindings(selectedKnowledgeBindings);
    setKnowledgeSearch('');
    setKnowledgeModalOpen(true);
  };

  const closeKnowledgeModal = () => {
    setKnowledgeModalOpen(false);
    setKnowledgeSearch('');
  };

  const confirmKnowledgeSelection = () => {
    setSelectedKnowledgeBindings(uniqueKnowledgeSelections(draftKnowledgeBindings));
    setKnowledgeModalOpen(false);
    setKnowledgeSearch('');
  };

  const toggleDraftKnowledgeItem = (item: KnowledgeItem) => {
    const selection = selectionFromKnowledgeItem(item);
    const key = knowledgeKey(selection);
    setDraftKnowledgeBindings(prev => {
      if (prev.some(existing => knowledgeKey(existing) === key)) {
        return prev.filter(existing => knowledgeKey(existing) !== key);
      }
      return uniqueKnowledgeSelections([...prev, selection]);
    });
  };

  const applySelections = (items: KnowledgeSelection[], shouldSelect: boolean) => {
    setDraftKnowledgeBindings(prev => {
      const next = new Map(prev.map(item => [knowledgeKey(item), item]));
      items.forEach(item => {
        const key = knowledgeKey(item);
        if (shouldSelect) {
          next.set(key, item);
        } else {
          next.delete(key);
        }
      });
      return Array.from(next.values());
    });
  };

  const toggleCurrentKnowledgeBaseSelection = () => {
    const items = filteredKnowledgeCatalog.map(selectionFromKnowledgeItem);
    if (items.length === 0) return;
    applySelections(items, !currentVisibleKnowledgeSelected);
  };

  const toggleDirectorySelection = (node: KnowledgeTreeNode) => {
    const items = collectDirectoryFiles(node).map(selectionFromKnowledgeItem);
    const shouldSelect = items.some(item => !draftKnowledgeSet.has(knowledgeKey(item)));
    applySelections(items, shouldSelect);
  };

  const removeSelectedKnowledge = (key: string) => {
    setSelectedKnowledgeBindings(prev => prev.filter(item => knowledgeKey(item) !== key));
  };

  const clearSelectedKnowledge = () => {
    setSelectedKnowledgeBindings([]);
  };

  const toggleDirectoryExpanded = (key: string) => {
    setExpandedDirectoryKeys(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const submit = async () => {
    const trimmedModelName = (form.model_binding.model_name || '').trim();
    if (!form.model_binding.inherited && !trimmedModelName) {
      setError('关闭“继承系统默认模型”后，必须提供覆盖模型名。');
      return;
    }

    setSaving(true);
    setError('');
    try {
      const knowledgeBindings = selectedKnowledgeBindings.map(item => ({
        kb_id: item.kb_id || null,
        knowledge_object_id: item.knowledge_object_id,
        knowledge_version_id: item.knowledge_version_id || null,
        title: item.title || null,
        type: item.type || null,
      }));

      const modelBindingPayload: Record<string, unknown> = {
        temperature: form.model_binding.temperature,
        max_tokens: form.model_binding.max_tokens,
        fallback_enabled: Boolean(form.model_binding.fallback_enabled),
        inherited: Boolean(form.model_binding.inherited),
      };
      if (!form.model_binding.inherited && trimmedModelName) {
        modelBindingPayload.model_name = trimmedModelName;
      }

      const payload: Record<string, unknown> = {
        name: form.name,
        bio: form.bio,
        tags: form.tagsText.split(/[、,\n]/).map(item => item.trim()).filter(Boolean),
        main_duty_cluster: form.main_duty_cluster || null,
        point_of_view: form.point_of_view || null,
        decision_style: form.decision_style || null,
        identity_background: form.identity_background || null,
        speaking_style: form.speaking_style || null,
        knowledge_boundary: knowledgeBindings.length > 0 ? form.knowledge_boundary || null : null,
        knowledge_bindings: knowledgeBindings,
        data_asset_binding_ids: form.data_asset_binding_ids,
        output_mode: form.output_mode,
        output_type: form.output_mode === 'structured' ? form.output_type || null : null,
        output_schema: form.output_mode === 'structured' ? parseJsonOrThrow(form.output_schema_text) : null,
        category: form.suggested_category || '自定义',
        business_domain: form.suggested_business_domain || null,
        model_binding: modelBindingPayload,
      };

      let saved: RoleDetail;
      if (isCreate) {
        saved = await api.createRole(payload, draftBriefing ? 'ai_assisted' : 'manual');
      } else {
        saved = await api.updateRole(id!, payload);
      }

      setRole(saved);
      setSelectedKnowledgeBindings(saved.knowledge_refs.map(selectionFromKnowledgeRef));
      navigate(`/roles/${saved.role_id}/edit`, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败，请检查结构化输出 JSON 是否正确');
    } finally {
      setSaving(false);
    }
  };

  const renderKnowledgeFile = (item: KnowledgeItem, depth = 0) => {
    const selected = draftKnowledgeSet.has(knowledgeKey(item));
    const relativePath = relativeKnowledgePath(item.knowledge_object_id, currentKnowledgeBase?.name);
    return (
      <button
        key={`${item.kb_id}-${item.knowledge_object_id}`}
        className={`file-row ${selected ? 'selected' : ''}`}
        type="button"
        onClick={() => toggleDraftKnowledgeItem(item)}
        style={{ paddingLeft: `${14 + depth * 18}px` }}
      >
        <span className="file-check" aria-hidden="true">
          {selected ? <Check size={14} /> : null}
        </span>
        <span className="file-copy">
          <strong>{item.title || fallbackKnowledgeTitle(relativePath)}</strong>
          <small>{relativePath}</small>
          <em>{item.summary || '暂无摘要'}</em>
        </span>
      </button>
    );
  };

  const renderKnowledgeDirectory = (node: KnowledgeTreeNode, depth = 0) => {
    const dirFiles = collectDirectoryFiles(node);
    const selectedCount = dirFiles.filter(item => draftKnowledgeSet.has(knowledgeKey(item))).length;
    const allSelected = dirFiles.length > 0 && selectedCount === dirFiles.length;
    const partiallySelected = selectedCount > 0 && !allSelected;
    const key = directoryKey(selectedKbId, node.path);
    const expanded = knowledgeSearch.trim() ? true : expandedDirectoryKeys.has(key);

    return (
      <div key={key} className="knowledge-tree-node">
        <div
          className={`directory-row ${allSelected ? 'selected' : partiallySelected ? 'partial' : ''}`}
          style={{ paddingLeft: `${14 + depth * 18}px` }}
        >
          <button
            className="tree-toggle-btn"
            type="button"
            onClick={() => toggleDirectoryExpanded(key)}
            aria-label={`${expanded ? '收起' : '展开'}目录 ${node.name}`}
            disabled={knowledgeSearch.trim().length > 0}
          >
            <ChevronDown
              size={16}
              style={{ transform: expanded ? 'rotate(0deg)' : 'rotate(-90deg)', transition: 'transform .16s ease' }}
            />
          </button>
          <div className="directory-copy">
            <strong>{node.name}</strong>
            <span>{dirFiles.length} 个文件</span>
          </div>
          <button
            className={`file-check ${allSelected ? 'selected' : partiallySelected ? 'partial' : ''}`}
            type="button"
            aria-label={`${allSelected ? '取消选择目录' : '选择目录'} ${node.name}`}
            onClick={() => toggleDirectorySelection(node)}
          >
            {allSelected ? <Check size={14} /> : partiallySelected ? '−' : null}
          </button>
          <span className="directory-meta">{selectedCount}/{dirFiles.length}</span>
        </div>
        {expanded && (
          <div className="directory-branch">
            {node.directories.map(child => renderKnowledgeDirectory(child, depth + 1))}
            {node.files.map(file => renderKnowledgeFile(file, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div className="page-loading">正在加载角色定义工作台...</div>;

  return (
    <div className="page">
      <Link className="back-link" to={role ? `/roles/${role.role_id}` : '/'}><ArrowLeft size={16} />返回</Link>

      <div className="page-head">
        <div>
          <p className="eyebrow">Role Definition Workbench</p>
          <h1>{isCreate ? '新建角色定义工作台' : `${role?.name || '角色'} · 角色定义工作台`}</h1>
          <p className="subtle">
            这一页只处理角色本体：L1 身份与判断、L2 知识依据、L3 数据能力、L4 输出方式与运行配置。
          </p>
        </div>
        <div className="button-row">
          <button className="primary-btn" onClick={submit} disabled={saving}>
            <Save size={16} />
            {saving ? '保存中...' : '保存草稿'}
          </button>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}
      {draftNote && <div className="collapsed-note"><Sparkles size={16} />{draftNote}</div>}

      <div className="role-page-grid">
        {role ? (
          <RoleStageNav roleId={role.role_id} />
        ) : (
          <aside className="role-stage-nav">
            <div className="role-stage-head">
              <p className="eyebrow">Before Save</p>
              <strong>先形成 draft 角色骨架</strong>
              <span>保存草稿后先进入 02 使用前说明与调用预览；保存当前说明后，再进入 03 试用与测试。</span>
            </div>
          </aside>
        )}

        <div className="role-page-main">
          <section className="form-section">
            <div className="section-title-row">
              <div>
                <h2><Wand2 size={16} />AI 协作创建</h2>
                <p className="section-intro">自然语言先生成结构化草案，但不会直接落库，也不会自动绑定真实知识或数据资产。</p>
              </div>
              <button className="secondary-btn" onClick={generateDraft} disabled={isDraftGenerating || !intentText.trim()}>
                {isDraftGenerating ? '生成中...' : '生成结构化草案'}
              </button>
            </div>
            <textarea
              rows={4}
              value={intentText}
              onChange={e => setIntentText(e.target.value)}
              placeholder="例如：我想创建一个能帮助集团管理层做经营复盘和投资前置判断的角色，它要基于已绑定知识和经营指标，输出可复用的建议与风险提示。"
            />
            {hasAIGovernanceSuggestion && (
              <div className="collapsed-note">
                <Sparkles size={16} />
                <span>
                  AI 当前建议的治理信息：分类 {form.suggested_category || '未给出'}，
                  业务域 {form.suggested_business_domain || '未给出'}。这些信息会随保存写入角色，并可在治理页继续调整。
                </span>
              </div>
            )}
          </section>

          <section className="form-section">
            <div className="section-title-row">
              <div>
                <h2>L1 身份与判断</h2>
                <p className="section-intro">主路径只保留名称、摘要、核心职责和分析视角；其余项进入高级设置。</p>
              </div>
              <button className="secondary-btn small-btn" onClick={() => setShowL1Advanced(prev => !prev)}>
                <ChevronDown size={14} />
                {showL1Advanced ? '收起高级项' : '展开高级项'}
              </button>
            </div>

            <div className="two-col">
              <label className="field-block">
                <span className="field-label">角色名称</span>
                <input value={form.name} onChange={e => onField('name', e.target.value)} placeholder="例如：经营分析顾问" />
              </label>
              <label className="field-block">
                <span className="field-label">一句话摘要</span>
                <textarea rows={3} value={form.bio} onChange={e => onField('bio', e.target.value)} placeholder="例如：面向管理层经营复盘场景，提供分析判断、建议草案与风险提示。" />
              </label>
            </div>

            <label className="field-block">
              <span className="field-label">核心职责</span>
              <textarea rows={3} value={form.main_duty_cluster} onChange={e => onField('main_duty_cluster', e.target.value)} placeholder="例如：围绕经营复盘与投资前置分析，负责识别关键经营问题、解释原因，并输出建议草案与风险提示。" />
            </label>

            <label className="field-block">
              <span className="field-label">分析视角</span>
              <textarea rows={3} value={form.point_of_view} onChange={e => onField('point_of_view', e.target.value)} placeholder="例如：优先从目标、约束和关键指标变化看问题，重点识别结果偏差背后的经营原因。" />
            </label>

            {showL1Advanced && (
              <div className="two-col">
                <label className="field-block">
                  <span className="field-label">决策风格（高级项）</span>
                  <input value={form.decision_style} onChange={e => onField('decision_style', e.target.value)} placeholder="例如：先澄清前提，再给平衡判断。" />
                </label>
                <label className="field-block">
                  <span className="field-label">身份背景（高级项）</span>
                  <textarea rows={3} value={form.identity_background} onChange={e => onField('identity_background', e.target.value)} placeholder="例如：具备跨部门经营分析与投前评估经验，熟悉管理层决策资料组织方式。" />
                </label>
                <label className="field-block span-2">
                  <span className="field-label">表达风格（高级项）</span>
                  <textarea rows={3} value={form.speaking_style} onChange={e => onField('speaking_style', e.target.value)} placeholder="例如：先给结论，再给依据和限制，语言保持简洁、克制、可供汇报复用。" />
                </label>
              </div>
            )}
          </section>

          <section className="form-section knowledge-summary-section">
            <div className="section-title-row">
              <div>
                <h2><BookOpen size={16} />L2 知识依据</h2>
                <p className="section-intro">支持“绑定真实知识”和“暂不绑定真实知识”两条合法路径；工作台里先选择，保存草稿时一并生效。</p>
              </div>
              <div className="button-row">
                <button className="secondary-btn small-btn" type="button" onClick={openKnowledgeModal}>
                  {hasSelectedKnowledge ? '编辑知识选择' : '选择真实知识'}
                </button>
                <button className="secondary-btn small-btn" type="button" onClick={clearSelectedKnowledge} disabled={!hasSelectedKnowledge}>
                  暂不绑定真实知识
                </button>
              </div>
            </div>

            <div className="knowledge-stats">
              <div>
                <strong>{selectedKnowledgeBindings.length}</strong>
                <span>已选文件数</span>
              </div>
              <div>
                <strong>{selectedKnowledgeGroups.length}</strong>
                <span>涉及知识库数</span>
              </div>
              <div>
                <strong>{currentKnowledgeBase?.name || '未选择'}</strong>
                <span>当前浏览知识库</span>
              </div>
            </div>

            {selectedKnowledgeGroups.length > 0 ? (
              <div className="selected-knowledge-groups">
                {selectedKnowledgeGroups.map(group => (
                  <div key={group.kbId} className="selected-knowledge-card">
                    <header>
                      <div>
                        <strong>{group.kbName}</strong>
                        <span>{group.items.length} 个文件</span>
                      </div>
                    </header>
                    <div className="selected-knowledge-list">
                      {group.items.map(item => {
                        const key = knowledgeKey(item);
                        const displayPath = relativeKnowledgePath(item.knowledge_object_id, knowledgeBaseNameMap[group.kbId]);
                        return (
                          <div key={key} className="selected-knowledge-item">
                            <div className="selected-knowledge-copy">
                              <strong>{item.title || fallbackKnowledgeTitle(displayPath)}</strong>
                              <small>{displayPath}</small>
                              <p>{item.summary || '保存时将按文件级 knowledge_refs 写入当前可编辑版本。'}</p>
                            </div>
                            <button className="text-toggle-btn" type="button" onClick={() => removeSelectedKnowledge(key)}>
                              移除
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="knowledge-empty-state">
                当前暂不绑定真实知识。你仍可保存草稿；若后续需要真实知识支持，再回到这里选择文件并保存。
              </div>
            )}

            <label className="field-block">
              <span className="field-label">知识边界</span>
              <textarea
                rows={3}
                value={form.knowledge_boundary}
                onChange={e => onField('knowledge_boundary', e.target.value)}
                placeholder="例如：基于已绑定制度与历史案例回答，暂不覆盖外部公开事实和未授权专项资料。"
                disabled={!hasSelectedKnowledge}
              />
              <span className="field-note">
                {hasSelectedKnowledge
                  ? '只有已选真实知识会参与保存；按目录勾选最终仍落为文件级 knowledge_refs。'
                  : '未绑定真实知识时不可编辑；若直接保存，knowledge_boundary 会自动归零为 null。'}
              </span>
            </label>
          </section>

          <section className="form-section">
            <div className="section-title-row">
              <div>
                <h2><Database size={16} />L3 数据能力（可选）</h2>
                <p className="section-intro">角色页只做绑定选择；数据资产由管理员在独立页面维护。</p>
              </div>
              <Link className="text-link" to="/data-assets">打开数据资产管理</Link>
            </div>

            <div className="data-asset-picker">
              {dataAssets.map(asset => {
                const selected = form.data_asset_binding_ids.includes(asset.id);
                return (
                  <button key={asset.id} className={`data-asset-card ${selected ? 'active' : ''}`} onClick={() => {
                    setForm(prev => ({
                      ...prev,
                      data_asset_binding_ids: prev.data_asset_binding_ids.includes(asset.id)
                        ? prev.data_asset_binding_ids.filter(id => id !== asset.id)
                        : [...prev.data_asset_binding_ids, asset.id],
                    }));
                  }}>
                    <strong>{asset.display_name}</strong>
                    <small>{asset.database_name}.{asset.table_name}</small>
                    <span>{asset.scope_summary}</span>
                  </button>
                );
              })}
              {dataAssets.length === 0 && (
                <div className="data-asset-empty-state">当前还没有可绑定的数据资产，请先去管理员页配置。</div>
              )}
            </div>

            {selectedAssets.length > 0 && (
              <div className="selected-asset-summary">
                {selectedAssets.map(asset => (
                  <div key={asset.id} className="selected-asset-card">
                    <strong>{asset.display_name}</strong>
                    <span>{asset.scope_summary}</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="form-section">
            <div className="section-title-row">
              <div>
                <h2>L4 输出方式与运行配置</h2>
                <p className="section-intro">默认合法路径是自由输出；只有选择结构化输出，模板和 schema 才进入主路径。</p>
              </div>
              <button className="secondary-btn small-btn" onClick={() => setShowL4Advanced(prev => !prev)}>
                <ChevronDown size={14} />
                {showL4Advanced ? '收起高级设置' : '展开高级设置'}
              </button>
            </div>

            <div className="segmented">
              <button className={form.output_mode === 'freeform' ? 'active' : ''} onClick={() => onField('output_mode', 'freeform')}>
                {outputModeText.freeform}
              </button>
              <button className={form.output_mode === 'structured' ? 'active' : ''} onClick={() => onField('output_mode', 'structured')}>
                {outputModeText.structured}
              </button>
            </div>

            {form.output_mode === 'structured' && (
              <>
                <div className="template-library">
                  {Object.entries(templates).map(([key, template]) => (
                    <button
                      key={key}
                      className={`template-card ${form.output_type === key ? 'active' : ''}`}
                      onClick={() => {
                        onField('output_type', key);
                        onField('output_schema_text', JSON.stringify(template.fields || {}, null, 2));
                      }}
                    >
                      <strong>{template.label || outputTypeText[key] || key}</strong>
                      <span>{key}</span>
                      <p>{Object.keys(template.fields || {}).join(' / ')}</p>
                    </button>
                  ))}
                </div>

                <label className="field-block">
                  <span className="field-label">角色级业务字段扩展 / 输出契约草案</span>
                  <textarea rows={10} value={form.output_schema_text} onChange={e => onField('output_schema_text', e.target.value)} placeholder='例如：{"position":"","key_reasons":[],"major_risks":[],"suggested_actions":[],"references":[]}' />
                </label>
              </>
            )}

            {showL4Advanced && (
              <div className="two-col">
                <label className="field-block">
                  <span className="field-label">当前运行提供方</span>
                  <input value={form.model_binding.model_provider || '由系统统一控制'} readOnly disabled />
                  <span className="field-note">模型提供方由系统统一控制，角色级不单独配置。</span>
                </label>
                <label className="field-block field-inline">
                  <input type="checkbox" checked={form.model_binding.inherited || false} onChange={e => onModelField('inherited', e.target.checked)} />
                  <span>继承系统默认模型</span>
                </label>
                <label className="field-block">
                  <span className="field-label">覆盖模型名</span>
                  <input
                    value={form.model_binding.model_name || ''}
                    onChange={e => onModelField('model_name', e.target.value)}
                    placeholder="例如：deepseek-v4-pro"
                    disabled={Boolean(form.model_binding.inherited)}
                  />
                  <span className="field-note">
                    {form.model_binding.inherited
                      ? '当前使用系统默认模型；取消勾选后才可覆盖模型名。'
                      : '只在明确需要时覆盖模型名；留空将无法保存。'}
                  </span>
                </label>
                <label className="field-block">
                  <span className="field-label">temperature</span>
                  <input type="number" step="0.1" min="0" max="2" value={form.model_binding.temperature} onChange={e => onModelField('temperature', Number(e.target.value))} />
                </label>
                <label className="field-block">
                  <span className="field-label">max_tokens</span>
                  <input type="number" min="1" value={form.model_binding.max_tokens} onChange={e => onModelField('max_tokens', Number(e.target.value))} />
                </label>
                <label className="field-block field-inline">
                  <input type="checkbox" checked={form.model_binding.fallback_enabled || false} onChange={e => onModelField('fallback_enabled', e.target.checked)} />
                  <span>允许运行时回退</span>
                </label>
              </div>
            )}
          </section>
        </div>

        <aside className="summary-rail">
          <section className="detail-section">
            <h2>当前摘要</h2>
            <dl>
              <dt>输出方式</dt>
              <dd>{outputModeText[form.output_mode]}</dd>
              <dt>治理建议分类</dt>
              <dd>{form.suggested_category || '未建议'}</dd>
              <dt>治理建议业务域</dt>
              <dd>{form.suggested_business_domain || '未建议'}</dd>
              <dt>已选知识</dt>
              <dd>{hasSelectedKnowledge ? `${selectedKnowledgeBindings.length} 个文件 / ${selectedKnowledgeGroups.length} 个知识库` : '当前未绑定真实知识'}</dd>
              <dt>已选数据资产</dt>
              <dd>{form.data_asset_binding_ids.length > 0 ? `${form.data_asset_binding_ids.length} 条` : '当前未授权'}</dd>
            </dl>
          </section>

          {role && (
            <section className="detail-section">
              <h2>工作区进度</h2>
              <div className="mini-check-list">
                {role.definition_progress.map(item => (
                  <div key={item.key} className={`mini-check ${item.state}`}>
                    <div>
                      <strong>{item.label}</strong>
                      <span>{item.detail}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </aside>
      </div>

      {knowledgeModalOpen && (
        <div className="modal-backdrop" onClick={closeKnowledgeModal}>
          <div className="knowledge-modal" onClick={event => event.stopPropagation()}>
            <div className="knowledge-modal-header">
              <div>
                <h2><BookOpen size={16} />选择真实知识</h2>
                <p className="section-intro">一次只浏览一个知识库，选择结果可跨知识库累积；保存时统一写成文件级 knowledge_refs。</p>
              </div>
              <button className="secondary-btn small-btn" type="button" onClick={closeKnowledgeModal}>
                <X size={14} />
                关闭
              </button>
            </div>

            <div className="knowledge-modal-toolbar">
              <label className="field-block knowledge-base-select">
                <span className="field-label">知识库</span>
                <select value={selectedKbId} onChange={e => setSelectedKbId(e.target.value)}>
                  {knowledgeBases.map(item => <option key={item.kb_id} value={item.kb_id}>{item.name}</option>)}
                </select>
              </label>

              <div className="search-box knowledge-search-box">
                <Search size={16} />
                <input
                  type="search"
                  value={knowledgeSearch}
                  onChange={e => setKnowledgeSearch(e.target.value)}
                  placeholder="搜索标题、路径、摘要或 tags"
                />
              </div>

              <div className="knowledge-toolbar-meta">
                <span>临时已选 {draftKnowledgeBindings.length} 个文件</span>
                <span>跨 {new Set(draftKnowledgeBindings.map(item => item.kb_id || 'unknown')).size} 个知识库</span>
              </div>
            </div>

            <div className="knowledge-browser-note">
              <span>目录级勾选会批量选中当前目录子树中的文件；搜索只影响当前可见节点，不会清空已选项。</span>
            </div>

            <div className="knowledge-browser">
              <div className="knowledge-base-panel">
                <div className="knowledge-base-header">
                  <button className="knowledge-base-toggle" type="button">
                    <BookOpen size={16} />
                    {currentKnowledgeBase?.name || '未发现知识库'}
                  </button>
                  <div className="knowledge-base-meta">
                    <span>当前视图 {currentVisibleKnowledgeCount} 个文件</span>
                    <button
                      className="secondary-btn small-btn"
                      type="button"
                      onClick={toggleCurrentKnowledgeBaseSelection}
                      disabled={currentVisibleKnowledgeCount === 0}
                    >
                      {currentVisibleKnowledgeSelected ? '取消当前知识库全选' : '当前知识库全选'}
                    </button>
                  </div>
                </div>

                <div className="knowledge-base-body">
                  {knowledgeCatalogLoading ? (
                    <div className="knowledge-empty-inline">正在加载知识目录...</div>
                  ) : currentVisibleKnowledgeCount === 0 ? (
                    <div className="knowledge-empty-inline">当前知识库下没有匹配的文件，可尝试切换知识库或调整搜索条件。</div>
                  ) : (
                    <>
                      {knowledgeTree.directories.map(node => renderKnowledgeDirectory(node))}
                      {knowledgeTree.files.map(item => renderKnowledgeFile(item))}
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="knowledge-modal-footer">
              <span>点击“完成选择”后才会回写到工作台；关闭或取消不会污染当前已确认选择。</span>
              <div className="button-row">
                <button className="secondary-btn" type="button" onClick={() => setDraftKnowledgeBindings([])} disabled={draftKnowledgeBindings.length === 0}>
                  清空选择
                </button>
                <button className="secondary-btn" type="button" onClick={closeKnowledgeModal}>
                  取消
                </button>
                <button className="primary-btn" type="button" onClick={confirmKnowledgeSelection}>
                  完成选择
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
