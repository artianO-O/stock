<template>
  <div v-show="show" class="live2d-wrapper">
    <canvas id="live2d" width="280" height="500" class="live2d"></canvas>
  </div>
</template>

<script setup>
import { onMounted, watch, nextTick } from 'vue'
import { withBase } from 'vitepress'

const props = defineProps({
  show: Boolean
})

const initLive2D = () => {
  if (window.loadlive2d) {
    loadRem()
    return
  }

  // 1. 加载 Live2D 核心驱动 (包含 loadlive2d 函数)
  const script = document.createElement('script')
  script.src = withBase('/live2d/live2d.js')
  script.async = true
  script.onload = () => {
    console.log('Live2D core loaded')
    loadRem()
  }
  document.body.appendChild(script)
}

const loadRem = () => {
  // 2. 加载雷姆模型 - 使用本地资源
  const modelUrl = withBase('/live2d/remu/model.json')
  
  nextTick(() => {
    const canvas = document.getElementById('live2d')
    if (canvas) {
      // 必须设置 user-select: none 否则可能无法点击交互
      canvas.style.userSelect = 'none'
      window.loadlive2d('live2d', modelUrl)
      console.log(`Loading Rem model from: ${modelUrl}`)
    }
  })
}

onMounted(() => {
  if (props.show) {
    initLive2D()
  }
})

watch(() => props.show, (val) => {
  if (val) {
    if (!window.loadlive2d) {
      initLive2D()
    } else {
      loadRem() 
    }
  }
})
</script>

<style scoped>
.live2d-wrapper {
  position: fixed;
  right: 20px;
  bottom: 0px;
  z-index: 999;
  pointer-events: none;
}

.live2d {
  width: 200px;
  height: 350px;
  pointer-events: auto;
}

@media (max-width: 768px) {
  .live2d-wrapper {
    display: none !important;
  }
}
</style>

