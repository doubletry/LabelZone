<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElButton, ElCard, ElTag } from 'element-plus'
import { messages, type Locale } from './i18n'

const locale = ref<Locale>('zh-CN')
const t = computed(() => messages[locale.value])

function toggleLocale() {
  locale.value = locale.value === 'zh-CN' ? 'en' : 'zh-CN'
}
</script>

<template>
  <main class="page-shell">
    <section class="hero">
      <div>
        <ElTag effect="dark">OAuth2 / OIDC</ElTag>
        <h1>{{ t.title }}</h1>
        <p>{{ t.subtitle }}</p>
      </div>
      <ElButton type="primary" @click="toggleLocale">{{ t.language }}</ElButton>
    </section>

    <section class="feature-grid" aria-label="LabelZone features">
      <ElCard shadow="hover"><strong>{{ t.sso }}</strong></ElCard>
      <ElCard shadow="hover"><strong>{{ t.storage }}</strong></ElCard>
      <ElCard shadow="hover"><strong>{{ t.annotation }}</strong></ElCard>
      <ElCard shadow="hover"><strong>{{ t.training }}</strong></ElCard>
    </section>

    <p class="font-note">{{ t.smoke }}</p>
  </main>
</template>
