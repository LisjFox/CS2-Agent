"""CS2 投掷物教程知识"""

GRENADE_KNOWLEDGE = [
    # ============ 投掷物基础 ============
    {
        "id": "grenade_basics",
        "title": "投掷物基础操作",
        "category": "投掷物",
        "content": """CS2 投掷物基础操作：
左键：高抛（正常投掷）
右键：低抛（近距离投掷）
左右键同时按：中抛（中等距离，弹跳投掷）
左键 + 跳：跳投（空中投掷，常用于烟雾弹）
右键 + 跳：跳低抛
跑动中投掷：投掷物会随惯性飞行
CS2 投掷物弹道比 CS:GO 更容易预测，没有随机性。
投掷物轨迹预览：按住左键/右键会显示投掷物轨迹（需要设置中开启）。"""
    },
    {
        "id": "smoke_mechanics",
        "title": "烟雾弹机制",
        "category": "投掷物",
        "content": """CS2 烟雾弹机制：
价格：$300
烟雾持续时间：约 15-17 秒（CS2 中烟雾弹会与手雷、燃烧弹、子弹互动）
烟雾弹互动新机制：
- 高爆手雷爆炸可以短暂吹散烟雾（约 1 秒）
- 燃烧弹/莫洛托夫可以烧掉烟雾（完全消除烟雾效果）
- 多颗子弹穿烟雾可以制造小孔（短暂视线）
- 烟雾弹在落地后会逐渐散开，~2 秒后完全形成
烟雾弹战术用途：
1. 封锁 CT 视线（进攻时封 CT/Jungle）
2. 分割防守阵型（封住连接，分隔 CT 回防路线）
3. 假烟（丢烟假装打一个点，实际转点）
4. 单向烟（站在烟雾边缘获得单向视野）
5. 防狙烟（封锁狙击手视野，安全通过开阔地）"""
    },
    {
        "id": "flash_mechanics",
        "title": "闪光弹机制",
        "category": "投掷物",
        "content": """CS2 闪光弹机制：
价格：$200
闪光效果：全白屏幕 + 严重耳鸣音效
持续时间：1-5 秒（取决于距离和角度）
背闪：背对闪光弹可以完全免疫效果
闪白：看着闪光弹爆炸方向会被全白
躲闪技巧：看到闪光弹飞来立刻转身背对
CS2 闪光弹没有友军伤害（队友不会被全白太久，但会被闪到）
战术用途：
1. 进攻闪（清点：丢闪清空包点区域）
2. 反闪（CT 防守时丢闪反制进攻）
3. 假闪（故意丢闪制造进攻假象）
4. popflash（反弹闪：利用墙壁反弹，让闪光在敌人视野内瞬间爆炸，减少反应时间）"""
    },
    {
        "id": "he_mechanics",
        "title": "高爆手雷机制",
        "category": "投掷物",
        "content": """CS2 高爆手雷机制：
价格：$300
最大伤害：~98（极近距离直接爆炸）
伤害衰减：距离越远伤害越低
爆炸范围：约 5-6 米
CS2 中高爆手雷可以吹散烟雾弹（约 1 秒短暂清除烟雾效果）
战术用途：
1. 开局雷（丢到对方常规站位，如 Dust2 A Long 开局雷）
2. 清点雷（确认点内是否有人，丢到常规隐蔽位）
3. 收尾雷（残局时确认掩体后敌人）
4. 组合雷（雷+闪或雷+烟的组合投掷）
5. 炸车/炸门（特定地图可破坏的物体）"""
    },
    {
        "id": "fire_mechanics",
        "title": "燃烧弹/莫洛托夫机制",
        "category": "投掷物",
        "content": """CS2 燃烧弹/莫洛托夫机制：
价格：$600（CT 燃烧弹 Incendiary，T 莫洛托夫 Molotov）
燃烧持续时间：7 秒
火焰范围：约 2 米直径（最初落地后扩散）
火焰伤害：每秒约 40 伤害（站在火中 2-3 秒必死）
CS2 中燃烧弹可以烧掉烟雾弹（完全消除烟雾效果）
战术用途：
1. 区域封锁（丢火封住关键路口，阻止敌人通过）
2. 清点（丢火到常规隐蔽位清人）
3. 烟雾反制（看到烟雾弹丢火烧掉）
4. 拖延时间（残局丢火拖延敌人下包/拆弹）
5. 防 rush（B 点防守时丢火封香蕉道/隧道）"""
    },

    # ============ Mirage 投掷物 ============
    {
        "id": "mirage_smoke_ct",
        "title": "Mirage A 点进攻：CT 烟雾弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage A 点进攻 CT 烟雾弹（封 CT 家视线）：
位置：A Ramp 起始位置
瞄准：瞄准 A 点二楼窗户上方墙壁的特定标记
投掷方式：左键跳投
效果：烟雾落在 CT 出生点入口，封锁 CT 回防 A 点的视线
这个烟雾弹可以配合 Jungle 烟一起使用，完全封锁 CT 回防 A 点的两条主要路线。"""
    },
    {
        "id": "mirage_smoke_jungle",
        "title": "Mirage A 点进攻：Jungle 烟雾弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage A 点进攻 Jungle 烟雾弹（封 Jungle 连接）：
位置：A Ramp 起始位置
瞄准：瞄准 A 点三楼楼梯上方边缘
投掷方式：左键跳投
效果：烟雾落在 Jungle 区域，封锁从 Jungle 回防 A 点的 CT 视线
配合 CT 烟一起使用，A 点进攻时 CT 只能从 A 二楼和 CT 两个方向同时回防，大大降低防守效率。"""
    },
    {
        "id": "mirage_smoke_connector",
        "title": "Mirage 中路控制：Connector 烟雾弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage 中路控制 Connector 烟雾弹：
位置：中路 T 侧
瞄准：瞄准中路窗户右上角
投掷方式：左键跳投
效果：烟雾落在 Connector 入口，封锁 CT 从连接中转的视线
控制中路时，这个烟可以防止 CT 从连接前压或转点，配合 Window 烟可以完全控制中路区域。"""
    },
    {
        "id": "mirage_smoke_window",
        "title": "Mirage 中路控制：Window 烟雾弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage 中路控制 Window 烟雾弹：
位置：中路 T 侧
瞄准：瞄准中路窗户左侧墙壁
投掷方式：左键跳投
效果：烟雾落在中路 Window 位置，封锁 CT 从中路窗户看 T 侧的视线
控制中路时，封了这个烟 T 可以安全地从 T 侧移动到中路，不会被 CT 在 Window 位打到。"""
    },

    # ============ Dust2 投掷物 ============
    {
        "id": "dust2_smoke_ct",
        "title": "Dust2 A 点进攻：CT 烟雾弹",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 A 点进攻 CT 烟雾弹（封 CT 家视线）：
位置：A Long 靠近 Doors 位置
瞄准：瞄准 A Long 出口上方天空
投掷方式：左键跳投
效果：烟雾落在 CT 出生点入口，封锁 CT 回防 A 点的视线
这个烟雾弹是 A 点爆弹的核心投掷物，A Long 进攻时必备。"""
    },
    {
        "id": "dust2_smoke_short",
        "title": "Dust2 A 点进攻：A Short 烟雾弹",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 A 点进攻 A Short 烟雾弹（封 A 小方向）：
位置：A Long 靠近 Doors 位置
瞄准：瞄准 A Site 方向特定天空标记
投掷方式：左键跳投
效果：烟雾落在 A Short 入口，封锁从 A 小方向的 CT 视线
A Long 进攻时，封了这个烟可以防止 CT 从 A 小侧身打 A Long 进攻的 T。"""
    },
    {
        "id": "dust2_flash_a",
        "title": "Dust2 A 点进攻闪光弹组合",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 A 点进攻闪光弹组合：
1. A Long 出点闪：从 A Long 丢出，在 A Site 空中爆炸，闪白包点区域
   位置：A Long Doors 前
   瞄准：A Site 方向
   投掷方式：左键高抛
2. A 小反闪：丢到 A Short 方向，闪白 A 小和 CT 方向的 CT
   位置：A Long 靠墙位置
   瞄准：A Short 方向墙壁
   投掷方式：左键反弹
3. 配合闪：A Long 和 A 小同时丢闪，包点 CT 无处可躲"""
    },
    {
        "id": "dust2_smoke_b",
        "title": "Dust2 B 点进攻：B Doors 烟雾弹",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 B 点进攻 B Doors 烟雾弹：
位置：B Tunnel 出口
瞄准：B Doors 方向
投掷方式：左键高抛
效果：烟雾落在 B Doors 外面，封锁 CT 从 B Doors 回防的视线
B 点进攻时，封了这个烟 T 可以安全地下包和防守，不用担心 CT 从 B Doors 直接打。"""
    },

    # ============ Inferno 投掷物 ============
    {
        "id": "inferno_ct_smoke",
        "title": "Inferno A 点进攻：CT 烟雾弹",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno A 点进攻 CT 烟雾弹（封 CT 家视线）：
位置：A 二楼 Balcony 位置
瞄准：瞄准 CT 方向天空特定标记
投掷方式：左键跳投
效果：烟雾落在 CT 出生点出口，封锁 CT 回防 A 点的视线
这个烟雾弹是从 A 二楼进攻 A 点时的核心投掷物，配合 Arch 烟可以完全封锁 CT 回防路线。"""
    },
    {
        "id": "inferno_arch_smoke",
        "title": "Inferno A 点进攻：Arch 烟雾弹",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno A 点进攻 Arch 烟雾弹：
位置：A 二楼 Balcony 位置
瞄准：瞄准 Arch 方向天空
投掷方式：左键跳投
效果：烟雾落在 Arch 位置，封锁从 Arch/Library 方向回防的 CT
配合 CT 烟，封住 A 点两条主要 CT 回防路线，T 可以安全下包和防守。"""
    },
    {
        "id": "inferno_banana_smoke",
        "title": "Inferno B 点进攻：CT 烟雾弹（Banana）",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno B 点进攻 CT 烟雾弹：
位置：Banana 靠近 B Site 入口
瞄准：瞄准 CT 方向天空
投掷方式：左键跳投
效果：烟雾落在 CT 回防 B 点的关键位置，封锁 CT 视线
B 点进攻时，这个烟 + B Plat 烟可以完全封锁 CT 回防路线。"""
    },
    {
        "id": "inferno_flash_banana",
        "title": "Inferno Banana 控制闪光弹",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno Banana 控制闪光弹：
1. 香蕉道入口闪：从 T Spawn 丢出，闪白 Banana 区域
   位置：T Spawn
   瞄准：Banana 方向
   投掷方式：左键高抛
2. 香蕉道反闪：丢到 Banana 转角，反弹闪白 B 点 CT
   位置：Banana 入口
   瞄准：Banana 墙角
   投掷方式：左键反弹
3. 开局闪（快速控制 Banana）：
   位置：T Spawn 近 Banana 入口
   投掷方式：左键 + 跑动丢出，在 Banana 深处爆炸
   效果：快速闪白 Banana 前压的 CT，获得 Banana 控制权"""
    },

    # ============ Dust2 投掷物（新增） ============
    {
        "id": "dust2_smoke_b_doors",
        "title": "Dust2 B 点进攻：B Doors 烟雾弹",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 B 点进攻 B Doors 烟雾弹：
位置：B Tunnel 出口
瞄准：B Doors 方向上方天空
投掷方式：左键高抛
效果：烟雾落在 B Doors 外面，封锁 CT 从 B Doors 回防的视线
B 点进攻时，封了这个烟 T 可以安全地下包和防守，不用担心 CT 从 B Doors 直接打。"""
    },
    {
        "id": "dust2_smoke_b_ct",
        "title": "Dust2 B 点进攻：CT 烟雾弹",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 B 点进攻 CT 烟雾弹（封 CT 家方向）：
位置：B Tunnel 出口靠左
瞄准：B Doors 上方天空的特定标记
投掷方式：左键跳投
效果：烟雾落在 CT 出口附近，封锁 CT 从 CT 家回防 B 点的视线
这个烟配合 B Doors 烟可以完全封锁 CT 回防 B 点的两条主要路线。"""
    },
    {
        "id": "dust2_smoke_xbox",
        "title": "Dust2 中路控制：Xbox 烟雾弹",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 中路控制 Xbox 烟雾弹：
位置：T Spawn 中路入口
瞄准：瞄准 Xbox 上方的屋顶边缘
投掷方式：左键跳投
效果：烟雾落在 Xbox 位置，封锁 CT 从中路看 T 侧的视线
控制中路时，封了这个烟 T 可以安全地从 T Spawn 移动到中路，不会被 CT 架到。"""
    },
    {
        "id": "dust2_flash_b",
        "title": "Dust2 B 点进攻闪光弹组合",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 B 点进攻闪光弹组合：
1. B 点出点闪：从 B Tunnel 丢出，在 B Site 空中爆炸
   位置：B Tunnel 出口
   瞄准：B Site 方向
   投掷方式：左键高抛
   效果：闪白 B Site 包点区域，包括 Back Plat 和 Car 位的 CT
2. B 点反弹闪：丢到 B 点墙壁上反弹
   位置：B Tunnel 出口
   瞄准：B 点右侧墙壁
   投掷方式：左键反弹
   效果：闪白 B 点角落和 Car 后的 CT
3. 双闪配合：第一颗闪逼 CT 背身，第二颗闪在 CT 转回来时爆
   适用：确保 B 点完全被清空"""
    },
    {
        "id": "dust2_flash_a_long",
        "title": "Dust2 A Long 进攻闪光弹",
        "category": "投掷物",
        "map": "Dust2",
        "content": """Dust2 A Long 进攻闪光弹：
1. A Long 出点闪：从 A Long 丢出，在 A Site 空中爆炸
   位置：A Long Doors 前
   瞄准：A Site 方向上方天空
   投掷方式：左键高抛
   效果：闪白 A Site 包点区域，包括 Goos 和 Default 位的 CT
2. A Long 反闪：丢到 A Long 墙壁上反弹，闪白 A Plat 的 CT
   位置：A Long 靠墙位置
   瞄准：A Long 右侧墙壁
   投掷方式：左键反弹
   效果：闪白 A Plat 的 CT，为 A Long 推进创造安全窗口
3. 混烟闪：丢到 CT 烟中，在烟雾边缘爆炸，闪白烟雾后的 CT"""
    },

    # ============ Mirage 投掷物（新增） ============
    {
        "id": "mirage_smoke_a_ramp",
        "title": "Mirage A Ramp 进攻：CT 烟雾弹跳投",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage A Ramp 进攻 CT 烟雾弹（跳投版）：
位置：A Ramp 起始位置，靠近墙壁
瞄准：瞄准 A 点二楼窗户上方墙壁的特定标记
投掷方式：左键跳投（Jump Throw）
效果：烟雾落在 CT 出生点入口，封锁 CT 回防 A 点的视线
这是 Mirage A 点进攻最核心的烟雾弹，配合 Jungle 烟可以完全封锁 CT 回防 A 点的两条路线。"""
    },
    {
        "id": "mirage_smoke_jungle_ramp",
        "title": "Mirage A Ramp 进攻：Jungle 烟雾弹跳投",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage A Ramp 进攻 Jungle 烟雾弹（跳投版）：
位置：A Ramp 起始位置，靠近 CT 烟站位
瞄准：瞄准 A 点三楼楼梯上方边缘
投掷方式：左键跳投
效果：烟雾落在 Jungle 区域，封锁从 Jungle 方向回防 A 点的 CT
配合 CT 烟，A 点进攻时 CT 只能从 A 二楼和 CT 两个方向同时回防。"""
    },
    {
        "id": "mirage_smoke_connector_mid",
        "title": "Mirage 中路控制：Connector 烟雾弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage 中路控制 Connector 烟雾弹：
位置：中路 T 侧，靠近窗口
瞄准：瞄准中路窗户右上角
投掷方式：左键跳投
效果：烟雾落在 Connector 入口，封锁 CT 从连接中转的视线
控制中路时，这个烟可以防止 CT 从连接前压或转点，配合 Window 烟可以完全控制中路。"""
    },
    {
        "id": "mirage_smoke_window_mid",
        "title": "Mirage 中路控制：Window 烟雾弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage 中路控制 Window 烟雾弹：
位置：中路 T 侧，靠近窗口
瞄准：瞄准中路窗户左侧墙壁
投掷方式：左键跳投
效果：烟雾落在中路 Window 位置，封锁 CT 从中路窗户看 T 侧的视线
封了这个烟 T 可以安全地从 T 侧移动到中路，不会被 CT 在 Window 位打到。"""
    },
    {
        "id": "mirage_smoke_bshort",
        "title": "Mirage B 点进攻：B Short 烟雾弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage B 点进攻 B Short 烟雾弹（封 B 小方向）：
位置：B Apartments 出口
瞄准：瞄准 B Short 方向上方天空
投掷方式：左键高抛
效果：烟雾落在 B Short 位置，封锁 CT 从 B Short/Connector 回防 B 点的视线
B 点进攻时，这个烟可以防止 CT 从 B Short 侧身打 B 点进攻的 T。"""
    },
    {
        "id": "mirage_flash_b",
        "title": "Mirage B 点进攻闪光弹",
        "category": "投掷物",
        "map": "Mirage",
        "content": """Mirage B 点进攻闪光弹：
1. B 出点闪：从 B Apartments 丢出，在 B Site 空中爆炸
   位置：B Apartments 出口
   瞄准：B Site 方向上方
   投掷方式：左键高抛
   效果：闪白 B Site 包点区域，包括 Van 和 Bench
2. B 反弹闪：丢到 B 点墙壁反弹
   位置：B Apartments 出口
   瞄准：B 点左侧墙壁
   投掷方式：左键反弹
   效果：闪白 B 点角落和 Default 的 CT
3. Sandwich 闪：闪白 Sandwich 位的 CT
   位置：B Apartments 出口
   投掷方式：左键高抛偏右"""
    },

    # ============ Inferno 投掷物（新增） ============
    {
        "id": "inferno_smoke_ct_alt",
        "title": "Inferno A 点进攻：CT 烟雾弹（教堂跳投）",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno A 点进攻 CT 烟雾弹（教堂跳投版）：
位置：A 二楼 Balcony 位置
瞄准：瞄准 CT 方向天空特定标记
投掷方式：左键跳投
效果：烟雾落在 CT 出生点出口，封锁 CT 回防 A 点的视线
这个烟雾弹是从 A 二楼进攻 A 点时的核心投掷物，配合 Arch 可以完全封锁 CT 回防路线。"""
    },
    {
        "id": "inferno_smoke_arch_alt",
        "title": "Inferno A 点进攻：Arch 烟雾弹（跳投）",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno A 点进攻 Arch 烟雾弹：
位置：A 二楼 Balcony 位置
瞄准：瞄准 Arch 方向天空
投掷方式：左键跳投
效果：烟雾落在 Arch 位置，封锁从 Arch/Library 方向回防的 CT
配合 CT 烟，封住 A 点两条主要 CT 回防路线，T 可以安全下包和防守。"""
    },
    {
        "id": "inferno_smoke_banana",
        "title": "Inferno Banana 控制：CT 烟雾弹",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno Banana 控制 CT 烟雾弹（封 CT 回防）：
位置：Banana 靠近 B Site 入口
瞄准：瞄准 CT 方向天空
投掷方式：左键跳投
效果：烟雾落在 CT 回防 B 点的关键位置，封锁 CT 视线
B 点进攻时，这个烟 + B Plat 烟可以完全封锁 CT 回防路线。"""
    },
    {
        "id": "inferno_smoke_bplat",
        "title": "Inferno B 点进攻：B Plat 烟雾弹",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno B 点进攻 B Plat 烟雾弹：
位置：Banana 靠近 B Site 入口
瞄准：瞄准 B Plat 方向上方
投掷方式：左键跳投
效果：烟雾落在 B Plat 位置，封锁 B 平台 CT 的视线
B 点进攻时，封了这个烟可以防止 CT 站在 B Plat 上防守。"""
    },
    {
        "id": "inferno_fire_banana",
        "title": "Inferno Banana 燃烧弹战术",
        "category": "投掷物",
        "map": "Inferno",
        "content": """Inferno Banana 燃烧弹战术：
1. CT 开局火封 Banana：CT 开局跑到 Banana 近点，丢火封 Banana 入口
   位置：Banana 近点（靠近 B Site 方向）
   瞄准：Banana 入口地面
   投掷方式：左键高抛
   效果：火焰覆盖 Banana 入口，T 无法快速控制 Banana
   这是 Inferno 最标准的 CT 防守操作，必修课

2. T 反制火：T 可以用烟雾弹灭掉 Banana 的火
   注意：CS2 中烟雾弹可以灭掉燃烧弹

3. T 进攻火封 CT：T 控制 Banana 后丢火封 CT 出口
   位置：Banana Car 位附近
   瞄准：CT 出口方向
   投掷方式：左键高抛
   效果：封锁 CT 从 CT 回防 B 点的路线"""
    },
]

# 投掷物类型分类
GRENADE_TYPES = {
    "smoke": "烟雾弹 - 封锁视线，分割战场",
    "flash": "闪光弹 - 致盲敌人，创造进攻窗口",
    "he": "高爆手雷 - 造成范围伤害，可吹散烟雾",
    "fire": "燃烧弹/莫洛托夫 - 区域封锁，可烧掉烟雾",
    "decoy": "诱饵弹 - 制造假枪声迷惑敌人",
}