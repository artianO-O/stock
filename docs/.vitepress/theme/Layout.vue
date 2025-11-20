<script setup>
import DefaultTheme from 'vitepress/theme'
import ParticleBackground from './components/ParticleBackground.vue'
import { useData } from 'vitepress'

const { Layout } = DefaultTheme
const { isDark } = useData()
</script>

<template>
  <Layout>
    <template #layout-bottom>
      <ClientOnly>
        <ParticleBackground v-if="!isDark" />
      </ClientOnly>
    </template>
  </Layout>
</template>

<style>
/* 确保布局背景透明，以便显示 Canvas */
html:not(.dark) .VPContent,
html:not(.dark) .VPFooter {
  background-color: transparent !important;
}
</style>

