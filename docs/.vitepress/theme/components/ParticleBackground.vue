<template>
  <div class="particle-background" ref="container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const container = ref(null)
const canvas = ref(null)
let ctx = null
let animationFrameId = null
let particles = []
let mouse = { x: null, y: null, radius: 150 }

// 配置参数
const config = {
  particleCount: 100, // 粒子数量
  color: 'rgba(124, 92, 235, 0.5)', // 粒子颜色
  lineColor: 'rgba(124, 92, 235, 0.15)', // 连线颜色
  lineWidth: 0.5,
  speed: 0.5, // 移动速度
  connectionDistance: 120, // 连线距离
  mouseRepelDistance: 150, // 鼠标排斥距离
  particleSize: { min: 1, max: 3 }
}

class Particle {
  constructor(w, h) {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.vx = (Math.random() - 0.5) * config.speed
    this.vy = (Math.random() - 0.5) * config.speed
    this.size = Math.random() * (config.particleSize.max - config.particleSize.min) + config.particleSize.min
  }

  draw() {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = config.color
    ctx.fill()
  }

  update(w, h) {
    // 边界检查
    if (this.x > w || this.x < 0) this.vx = -this.vx
    if (this.y > h || this.y < 0) this.vy = -this.vy

    // 鼠标排斥逻辑
    if (mouse.x != null) {
      let dx = mouse.x - this.x
      let dy = mouse.y - this.y
      let distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance < config.mouseRepelDistance) {
        const forceDirectionX = dx / distance
        const forceDirectionY = dy / distance
        const force = (config.mouseRepelDistance - distance) / config.mouseRepelDistance
        const directionX = forceDirectionX * force * 3 // 斥力强度
        const directionY = forceDirectionY * force * 3

        this.vx -= directionX
        this.vy -= directionY
      }
    }

    this.x += this.vx
    this.y += this.vy
    
    // 摩擦力，让粒子慢慢恢复正常速度
    // 简单模拟：限制最大速度
    const maxSpeed = config.speed * 5
    if (Math.abs(this.vx) > maxSpeed) this.vx *= 0.9
    if (Math.abs(this.vy) > maxSpeed) this.vy *= 0.9
    
    // 保证最小速度，防止停滞
    /* if (Math.abs(this.vx) < config.speed) this.vx = this.vx > 0 ? config.speed : -config.speed
    if (Math.abs(this.vy) < config.speed) this.vy = this.vy > 0 ? config.speed : -config.speed */

    this.draw()
  }
}

function init() {
  resize()
  particles = []
  const w = canvas.value.width
  const h = canvas.value.height
  // 根据屏幕面积动态调整粒子数量
  const count = Math.min(Math.floor((w * h) / 10000), 150)
  
  for (let i = 0; i < count; i++) {
    particles.push(new Particle(w, h))
  }
}

function animate() {
  if (!canvas.value) return
  const w = canvas.value.width
  const h = canvas.value.height
  ctx.clearRect(0, 0, w, h)
  
  for (let i = 0; i < particles.length; i++) {
    particles[i].update(w, h)
    
    // 连线
    for (let j = i; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance < config.connectionDistance) {
        ctx.beginPath()
        ctx.strokeStyle = config.lineColor
        ctx.lineWidth = config.lineWidth
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        ctx.stroke()
      }
    }
  }
  animationFrameId = requestAnimationFrame(animate)
}

function resize() {
  if (container.value && canvas.value) {
    canvas.value.width = container.value.offsetWidth
    canvas.value.height = container.value.offsetHeight
  }
}

function onMouseMove(e) {
  const rect = canvas.value.getBoundingClientRect()
  mouse.x = e.clientX - rect.left
  mouse.y = e.clientY - rect.top
}

function onMouseLeave() {
  mouse.x = null
  mouse.y = null
}

onMounted(() => {
  if (!canvas.value) return
  ctx = canvas.value.getContext('2d')
  window.addEventListener('resize', () => {
    resize()
    init() // resize 重置粒子，避免拉伸
  })
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseout', onMouseLeave)
  
  init()
  animate()
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseout', onMouseLeave)
  cancelAnimationFrame(animationFrameId)
})
</script>

<style scoped>
.particle-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1; /* 置于底层 */
  pointer-events: none; /* 允许点击穿透 */
  background: transparent;
}
</style>

