import { defineConfig } from 'vitepress'

export default defineConfig({
  // 如果仓库名不是 stock，请修改为你的仓库名，例如：'/your-repo-name/'
  // 如果使用自定义域名，可以设置为 '/'
  // 项目部署在 https://artiano-o.github.io/stock/，所以 base 设置为 '/stock/'
  base: '/stock/',
  title: '股票战法指南',
  description: '股票短线与趋势交易战法详解',
  
  // 外观设置 - 默认深色主题
  appearance: 'dark',
  
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
            { text: '超预期战法', link: '/short-term/超预期战法' },
            { text: '弱转强战法', link: '/short-term/弱转强战法' },
            { text: '爆量转一致战法', link: '/short-term/爆量转一致战法' },
            { text: '一红定江山战法', link: '/short-term/一红定江山战法' },
            { text: '仙人指路战法', link: '/short-term/仙人指路战法' },
            { text: '炸板低接战法', link: '/short-term/炸板低接战法' },
            { text: '竞价凹槽战法', link: '/short-term/竞价凹槽战法' },
            { text: '筹码空间博弈战法', link: '/short-term/筹码空间博弈战法' }
          ]
        }
      ],
      '/trend/': [
        {
          text: '趋势战法',
          items: [
            { text: '均线战法', link: '/trend/均线战法' },
            { text: 'N字战法', link: '/trend/N字战法' },
            { text: '首阴战法', link: '/trend/首阴战法' },
            { text: '三阳开泰战法', link: '/trend/三阳开泰战法' },
            { text: '趋势线战法', link: '/trend/趋势线战法' },
            { text: '量能突破战法', link: '/trend/量能突破战法' },
            { text: '波段操作战法', link: '/trend/波段操作战法' },
            { text: '龙头战法', link: '/trend/龙头战法' }
          ]
        }
      ],
      '/游资/': [
        {
          text: '知名游资心法',
          items: [
            {
              text: '退学炒股',
              link: '/游资/退学炒股',
              collapsed: false,
              items: [
                { text: '前言', link: '/游资/退学炒股#前言' },
                { text: '我和小明', link: '/游资/退学炒股#我和小明' },
                {
                  text: '交易心得与反思',
                  link: '/游资/退学炒股#交易心得与反思',
                  items: [
                    { text: '关于操作', link: '/游资/退学炒股#关于操作' },
                    { text: '关于心态', link: '/游资/退学炒股#关于心态' },
                    { text: '关于踏空', link: '/游资/退学炒股#关于踏空' },
                    { text: '关于空仓', link: '/游资/退学炒股#关于空仓' },
                    { text: '关于回撤', link: '/游资/退学炒股#关于回撤' },
                    { text: '关于分仓', link: '/游资/退学炒股#关于分仓' },
                    { text: '关于错误', link: '/游资/退学炒股#关于错误' },
                    { text: '关于学习', link: '/游资/退学炒股#关于学习' },
                    { text: '关于人性', link: '/游资/退学炒股#关于人性' },
                    { text: '关于市场', link: '/游资/退学炒股#关于市场' },
                    { text: '关于生活与理想', link: '/游资/退学炒股#关于生活与理想' }
                  ]
                },
                { text: '最后的对话', link: '/游资/退学炒股#最后的对话' },
                { text: '核心心法总结', link: '/游资/退学炒股#核心心法总结' }
              ]
            },
            {
              text: '炒股养家',
              link: '/游资/炒股养家',
              collapsed: false,
              items: [
                { text: '前言', link: '/游资/炒股养家#前言' },
                { text: '核心心法', link: '/游资/炒股养家#核心心法' },
                {
                  text: '市场情绪与心理',
                  link: '/游资/炒股养家#市场情绪与心理',
                  items: [
                    { text: '赚钱效应与亏钱效应', link: '/游资/炒股养家#赚钱效应与亏钱效应' },
                    { text: '贪婪与恐慌', link: '/游资/炒股养家#贪婪与恐慌' },
                    { text: '市场心理的把握', link: '/游资/炒股养家#市场心理的把握' }
                  ]
                },
                {
                  text: '操作策略',
                  link: '/游资/炒股养家#操作策略',
                  items: [
                    { text: '不同市场阶段的策略', link: '/游资/炒股养家#不同市场阶段的策略' },
                    { text: '弱势市场的操作', link: '/游资/炒股养家#弱势市场的操作' },
                    { text: '超跌度的把握', link: '/游资/炒股养家#超跌度的把握' },
                    { text: '市场不同阶段的应对', link: '/游资/炒股养家#市场不同阶段的应对' }
                  ]
                },
                {
                  text: '仓位管理',
                  link: '/游资/炒股养家#仓位管理',
                  items: [
                    { text: '仓位的基本原则', link: '/游资/炒股养家#仓位的基本原则' },
                    { text: '仓位与市场的关系', link: '/游资/炒股养家#仓位与市场的关系' },
                    { text: '重仓出击的条件', link: '/游资/炒股养家#重仓出击的条件' }
                  ]
                },
                {
                  text: '风险控制',
                  link: '/游资/炒股养家#风险控制',
                  items: [
                    { text: '控制回撤', link: '/游资/炒股养家#控制回撤' },
                    { text: '风险与收益的衡量', link: '/游资/炒股养家#风险与收益的衡量' },
                    { text: '操作原则', link: '/游资/炒股养家#操作原则' }
                  ]
                },
                {
                  text: '技术分析',
                  link: '/游资/炒股养家#技术分析',
                  items: [
                    { text: '技术的局限性', link: '/游资/炒股养家#技术的局限性' },
                    { text: '突破与大局观', link: '/游资/炒股养家#突破与大局观' },
                    { text: '板块与个股', link: '/游资/炒股养家#板块与个股' },
                    { text: '成交量', link: '/游资/炒股养家#成交量' }
                  ]
                },
                {
                  text: '龙头与热点',
                  link: '/游资/炒股养家#龙头与热点',
                  items: [
                    { text: '龙头理论', link: '/游资/炒股养家#龙头理论' },
                    { text: '龙头的选择', link: '/游资/炒股养家#龙头的选择' },
                    { text: '热点的判断', link: '/游资/炒股养家#热点的判断' },
                    { text: '次新股', link: '/游资/炒股养家#次新股' }
                  ]
                },
                {
                  text: '大局观',
                  link: '/游资/炒股养家#大局观',
                  items: [
                    { text: '大局观的重要性', link: '/游资/炒股养家#大局观的重要性' },
                    { text: '政策面与基本面', link: '/游资/炒股养家#政策面与基本面' },
                    { text: '看长做短', link: '/游资/炒股养家#看长做短' },
                    { text: '市场跟随', link: '/游资/炒股养家#市场跟随' }
                  ]
                },
                {
                  text: '操作心态',
                  link: '/游资/炒股养家#操作心态',
                  items: [
                    { text: '心态的重要性', link: '/游资/炒股养家#心态的重要性' },
                    { text: '操作原则', link: '/游资/炒股养家#操作原则-1' },
                    { text: '成本障碍', link: '/游资/炒股养家#成本障碍' }
                  ]
                },
                {
                  text: '交易系统',
                  link: '/游资/炒股养家#交易系统',
                  items: [
                    { text: '系统的建立', link: '/游资/炒股养家#系统的建立' },
                    { text: '操作时机', link: '/游资/炒股养家#操作时机' },
                    { text: '操作频率', link: '/游资/炒股养家#操作频率' }
                  ]
                },
                {
                  text: '职业炒股',
                  link: '/游资/炒股养家#职业炒股',
                  items: [
                    { text: '职业选择', link: '/游资/炒股养家#职业选择' },
                    { text: '职业标准', link: '/游资/炒股养家#职业标准' },
                    { text: '职业路径', link: '/游资/炒股养家#职业路径' }
                  ]
                },
                { text: '核心心法总结', link: '/游资/炒股养家#核心心法总结' }
              ]
            },
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

