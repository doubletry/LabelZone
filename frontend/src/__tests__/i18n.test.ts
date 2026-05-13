import { describe, expect, it } from 'vitest'
import { messages } from '../i18n'

describe('i18n messages', () => {
  it('contains bilingual product copy', () => {
    expect(messages.en.sso).toContain('OAuth2')
    expect(messages['zh-CN'].sso).toContain('单点登录')
  })
})
