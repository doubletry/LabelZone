import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it } from 'vitest'
import App from '../App.vue'

describe('App', () => {
  it('renders Chinese by default and toggles to English', async () => {
    const wrapper = mount(App, { global: { plugins: [ElementPlus] } })
    expect(wrapper.text()).toContain('LabelZone 标注平台')
    expect(wrapper.text()).toContain('避免中文乱码')
    await wrapper.find('button').trigger('click')
    expect(wrapper.text()).toContain('Private annotation')
  })
})
