<template>
  <canvas ref="canvas" class="particles-bg"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
let ctx = null
let particles = []
let animationFrameId = null
let mouse = { x: null, y: null, radius: 150 }

// 配置参数
const PARTICLE_COUNT = 100 // 粒子数量
const CONNECTION_DISTANCE = 120 // 连线距离
const MOUSE_DISTANCE = 150 // 鼠标互动距离

class Particle {
  constructor(w, h) {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.vx = (Math.random() - 0.5) * 1 // 速度
    this.vy = (Math.random() - 0.5) * 1
    this.size = Math.random() * 2 + 1
    // 浅色主题下的粒子颜色：淡蓝/淡紫
    this.color = `rgba(${100 + Math.random() * 100}, ${100 + Math.random() * 100}, 255, 0.6)` 
  }

  update(w, h) {
    this.x += this.vx
    this.y += this.vy

    // 边界检查
    if (this.x < 0 || this.x > w) this.vx *= -1
    if (this.y < 0 || this.y > h) this.vy *= -1

    // 鼠标互动
    if (mouse.x != null) {
      let dx = mouse.x - this.x
      let dy = mouse.y - this.y
      let distance = Math.sqrt(dx * dx + dy * dy)
      if (distance < MOUSE_DISTANCE) {
        const forceDirectionX = dx / distance
        const forceDirectionY = dy / distance
        const force = (MOUSE_DISTANCE - distance) / MOUSE_DISTANCE
        const directionX = forceDirectionX * force * 3
        const directionY = forceDirectionY * force * 3
        
        this.x -= directionX
        this.y -= directionY
      }
    }
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.fill()
  }
}

const init = () => {
  const w = window.innerWidth
  const h = window.innerHeight
  canvas.value.width = w
  canvas.value.height = h
  particles = []
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(new Particle(w, h))
  }
}

const animate = () => {
  if (!canvas.value) return
  const w = canvas.value.width
  const h = canvas.value.height
  ctx.clearRect(0, 0, w, h)

  for (let i = 0; i < particles.length; i++) {
    particles[i].update(w, h)
    particles[i].draw(ctx)

    // 连线
    for (let j = i; j < particles.length; j++) {
      let dx = particles[i].x - particles[j].x
      let dy = particles[i].y - particles[j].y
      let distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < CONNECTION_DISTANCE) {
        ctx.beginPath()
        // 线条颜色：浅灰偏蓝
        const opacity = 1 - distance / CONNECTION_DISTANCE
        ctx.strokeStyle = `rgba(150, 150, 200, ${opacity * 0.4})`
        ctx.lineWidth = 1
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        ctx.stroke()
      }
    }
  }
  animationFrameId = requestAnimationFrame(animate)
}

const handleResize = () => {
  init()
}

const handleMouseMove = (e) => {
  mouse.x = e.x
  mouse.y = e.y
}

const handleMouseLeave = () => {
  mouse.x = null
  mouse.y = null
}

onMounted(() => {
  if (canvas.value) {
    ctx = canvas.value.getContext('2d')
    init()
    animate()
    window.addEventListener('resize', handleResize)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseout', handleMouseLeave)
  }
})

onUnmounted(() => {
  cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseout', handleMouseLeave)
})
</script>

<style scoped>
.particles-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1; /* 放在最底层 */
  pointer-events: none; /* 不阻挡点击 */
  opacity: 0.8;
  /* 仅在浅色模式下显示较明显，深色模式可能需要调整 */
  transition: opacity 0.5s ease;
}

/* 在深色模式下降低不透明度或者隐藏，避免干扰 */
:global(.dark) .particles-bg {
  opacity: 0.2; 
}
</style>

