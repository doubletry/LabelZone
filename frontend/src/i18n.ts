export type Locale = 'en' | 'zh-CN'

export const messages = {
  en: {
    title: 'LabelZone',
    subtitle: 'Private annotation, export, and training queue platform',
    sso: 'Enterprise OAuth2 SSO',
    storage: 'Local storage first, RustFS optional',
    annotation: 'Classification, bounding box, and polygon annotation',
    training: 'GPU training queue integration',
    language: '中文',
    smoke: 'Chinese-safe screenshots use Noto Sans CJK / Microsoft YaHei fallback fonts.',
  },
  'zh-CN': {
    title: 'LabelZone 标注平台',
    subtitle: '私有化标注、导出与训练队列平台',
    sso: '企业 OAuth2 单点登录',
    storage: '优先本地存储，可选 RustFS',
    annotation: '分类、矩形框和多边形标注',
    training: 'GPU 训练队列集成',
    language: 'English',
    smoke: '运行截图使用 Noto Sans CJK / 微软雅黑等字体兜底，避免中文乱码。',
  },
} as const
