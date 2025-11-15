import { defineConfig } from 'vitepress'

export default defineConfig({
  // 如果仓库名不是 stock，请修改为你的仓库名，例如：'/your-repo-name/'
  // 如果使用自定义域名，可以设置为 '/'
  // 项目部署在 https://artiano-o.github.io/stock/，所以 base 设置为 '/stock/'
  base: '/stock/',
  title: '股票战法指南',
  description: '股票短线与趋势交易战法详解',
  
  // 主题配置
  themeConfig: {
    // 网站标题
    siteTitle: '股票战法指南',
    
    // 导航栏
    nav: [
      { text: '首页', link: '/' },
      { text: '短线战法', link: '/short-term/' },
      { text: '趋势战法', link: '/trend/' },
      { text: '知名游资', link: '/游资/' }
    ],
    
    // 侧边栏
    sidebar: {
      '/short-term/': [
        {
          text: '短线战法',
          items: [
            { text: '超预期战法', link: '/short-term/#1-超预期战法' },
            { text: '弱转强战法', link: '/short-term/#2-弱转强战法' },
            { text: '爆量转一致战法', link: '/short-term/#3-爆量转一致战法' },
            { text: '一红定江山战法', link: '/short-term/#4-一红定江山战法' },
            { text: '仙人指路战法', link: '/short-term/#5-仙人指路战法' },
            { text: '炸板低接战法', link: '/short-term/#6-炸板低接战法' },
            { text: '竞价凹槽战法', link: '/short-term/#7-竞价凹槽战法' },
            { text: '筹码空间博弈战法', link: '/short-term/#8-筹码空间博弈战法' }
          ]
        }
      ],
      '/trend/': [
        {
          text: '趋势战法',
          items: [
            { text: '均线战法', link: '/trend/#1-均线战法' },
            { text: 'N字战法', link: '/trend/#2-n字战法' },
            { text: '首阴战法', link: '/trend/#3-首阴战法' },
            { text: '三阳开泰战法', link: '/trend/#4-三阳开泰战法' },
            { text: '趋势线战法', link: '/trend/#5-趋势线战法' },
            { text: '量能突破战法', link: '/trend/#6-量能突破战法' },
            { text: '波段操作战法', link: '/trend/#7-波段操作战法' },
            { text: '龙头战法', link: '/trend/#8-龙头战法' }
          ]
        }
      ],
      '/游资/': [
        {
          text: '知名游资心法',
          items: [
            { text: '退学炒股', link: '/游资/退学炒股' },
            { text: '炒股养家', link: '/游资/炒股养家' },
            { text: '赵老哥', link: '/游资/赵老哥' },
            { text: '作手新一', link: '/游资/作手新一' },
            { text: '方新侠', link: '/游资/方新侠' },
            { text: '章建平', link: '/游资/章建平' }
          ]
        }
      ]
    },
    
    // 社交链接
    socialLinks: [],
    
    // 页脚
    footer: {
      message: '投资有风险，入市需谨慎',
      copyright: '© 2025 股票战法指南'
    },
    
    // 搜索
    search: {
      provider: 'local'
    },
    
    // 编辑链接
    editLink: {
      pattern: '',
      text: ''
    }
  }
})

