window.LEARN_BASICS = [
  {
    id: "py",
    title: "Python 基础",
    blurb: "列表、字典、异常、同步异步。先懂它是什么，再记面试怎么说。",
    steps: [
      {
        title: "list 和 tuple",
        why: "list 是清单，可以增删改，允许重复，适合「一批用户」。tuple 也是有顺序的一串东西，但通常不改，适合「固定的三个数」。面试别只说「一个可变一个不可变」，要补一句什么时候用哪个。",
        packet: "users = [\"张三\", \"李四\"]   # 以后还会加人\npoint = (10, 20)           # 坐标一般不改",
        q: "动态的用户名单应该用哪种？",
        options: ["tuple，因为更安全", "list，因为还要增删", "两种完全一样"],
        answer: 1,
        explain: "面试可以说：list 可变，适合会变化的数据；tuple 通常当固定结构。用户名单会增减，所以用 list。"
      },
      {
        title: "dict 字典",
        why: "字典是用名字找内容：key 是名字，value 是内容。接口里的 JSON、配置、一个用户的各个字段，几乎都是字典。它查找快，是因为内部用哈希把 key 映射到位置，一般不用从头扫。",
        packet: "user = {\"name\": \"张三\", \"age\": 20}\nuser[\"name\"]  →  张三",
        q: "为什么常说 dict 查找比较快？",
        options: [
          "它通过哈希把 key 映射到位置，平均不用从头遍历",
          "字典一定比列表占更少内存",
          "字典会自动建数据库索引"
        ],
        answer: 0,
        explain: "面试可以说：dict 用 key 直接定位，适合 JSON 和对象字段。不要说「因为它是哈希所以永远 O(1)」，极端情况也会变慢，但入门这样答就够。"
      },
      {
        title: "== 和 is",
        why: "== 问的是值相不相等。is 问的是是不是内存里同一个对象。判断「有没有」时，None 要用 is None，这是约定，也更稳。",
        packet: "a = [1, 2]\nb = [1, 2]\na == b   # True，值一样\na is b   # False，两个列表",
        q: "判断变量是不是 None，更合适的写法？",
        options: ["if x == None", "if x is None", "if x = None"],
        answer: 1,
        explain: "面试可以说：== 比内容，is 比是不是同一个对象。None 用 is。第三个选项是赋值，根本不是比较。"
      },
      {
        title: "浅拷贝和深拷贝",
        why: "拷贝是为了改一份副本，不影响原来的。浅拷贝只复制外层盒子，里面的小盒子还是共用的。深拷贝会连里面一起复制。嵌套列表、嵌套字典时最容易踩坑。",
        packet: "a = [[1], [2]]\nb = a.copy()     # 浅拷贝\nb[0].append(9)\n# a[0] 也会变成 [1, 9]，因为内层还是同一个列表",
        q: "什么时候必须用深拷贝？",
        options: [
          "只拷贝一层数字时",
          "数据有嵌套，改副本时不能动到原来的内层",
          "只要用了 copy 就一定是深拷贝"
        ],
        answer: 1,
        explain: "面试可以说：浅拷贝共享内层对象，深拷贝才完全独立。一维数字列表用浅拷贝通常没问题。"
      },
      {
        title: "函数和异常",
        why: "函数是把一段会重复的逻辑包起来，收参数、给结果。出错时不要让程序直接崩溃：用 try/except 接住，记下日志，给前端一句人能看懂的原因。参数错、网络失败，都该这样。",
        packet: "try:\n    age = int(text)\nexcept ValueError:\n    return \"年龄必须是数字\"",
        q: "用户把年龄填成「十八」，后端最合适的做法？",
        options: [
          "捕获错误并返回清楚原因，不要让整个服务崩掉",
          "假装成功，把年龄存成 0",
          "什么都不做，等数据库自己报错"
        ],
        answer: 0,
        explain: "面试可以说：可预期的错要变成明确错误信息；真正意外的错再记日志。不要吞掉错误假装成功。"
      },
      {
        title: "装饰器",
        why: "装饰器是「不改原函数内部代码，在外面加一层」。常见用途：先检查登录、打日志、统计耗时。你听过 @app.post，那就是 FastAPI 用装饰器把函数挂到路由上。",
        packet: "@app.post(\"/users\")\ndef create_user(...):\n    ...",
        q: "装饰器主要解决什么？",
        options: [
          "把 Python 编译成 JavaScript",
          "不改原函数代码，给它加上鉴权、日志等额外行为",
          "让数据库自动建表"
        ],
        answer: 1,
        explain: "面试可以说：装饰器是外包一层功能。FastAPI 的 @app.post 就是把函数登记成接口。"
      },
      {
        title: "生成器",
        why: "普通列表会一次把全部数据装进内存。生成器是「你要一个我才给一个」，适合读大文件、很多行记录。面试官问 yield，你就说：按需产生，省内存。",
        packet: "def lines():\n    for row in big_file:\n        yield row",
        q: "生成器最主要的好处？",
        options: [
          "一定比列表算得更快",
          "逐个产生数据，避免一次把全部装进内存",
          "可以代替数据库"
        ],
        answer: 1,
        explain: "面试可以说：生成器适合大数据流。小列表没必要硬上生成器。"
      },
      {
        title: "同步、异步、GIL",
        why: "同步：这件事没完，就干等。异步：等网络或数据库时，可以去处理别人的请求。网页接口经常在等 IO，所以 FastAPI 支持异步。GIL 的意思是：CPython 里同一进程通常只有一个线程在跑 Python 字节码，所以多线程不太能加速纯计算，更适合 IO 等待。",
        packet: "同步：排队打电话，说完才接下一个\n异步：打电话等对方时，先处理下一位",
        q: "调用远程 HTTP 接口这种「干等网络」的事，为什么常提异步？",
        options: [
          "异步能让 CPU 计算本身变快十倍",
          "等网络的空隙可以去处理其他请求",
          "有了异步就可以不用数据库"
        ],
        answer: 1,
        explain: "面试可以说：IO 等待适合异步或线程；纯计算常用多进程。GIL 让多线程难以加速纯 Python 计算。还要补一句：如果库本身是阻塞的，只把函数写成 async 不会自动变快。"
      }
    ]
  },
  {
    id: "http",
    title: "HTTP 与 REST",
    blurb: "方法、路径、状态码。接口就是前后端约好的窗口。",
    steps: [
      {
        title: "接口是什么",
        why: "接口不是一个按钮，是约定：前端按方法、地址、数据格式来叫，后端按状态码和 JSON 来回。两边只要有一方不按约定，联调就会失败。",
        packet: "前端：POST /users + JSON\n后端：201 + {\"id\": 17, \"name\": \"张三\"}",
        q: "接口最核心的含义？",
        options: [
          "前端和后端约定好的请求与响应格式",
          "数据库的别名",
          "Nginx 的配置文件"
        ],
        answer: 0,
        explain: "面试可以说：接口是前后端契约。方法、路径、字段名、状态码都要先对齐。"
      },
      {
        title: "一次请求有哪些部分",
        why: "方法说明想做什么。路径说明操作谁。查询参数适合筛选分页。请求头放格式和 Token。请求体放较复杂的 JSON。状态码说明结果类型。响应体是返回的数据。",
        packet: "GET /users?page=1&size=20\nAuthorization: Bearer <token>",
        q: "页码、每页条数通常放在哪里？",
        options: ["请求体 JSON 里（对 GET 也最常见）", "查询参数，例如 page 和 size", "只能放在 Cookie"],
        answer: 1,
        explain: "面试可以说：GET 用查询参数做筛选分页；POST/PUT 的复杂数据放请求体。"
      },
      {
        title: "GET 和 POST",
        why: "GET 用来读，不该改服务器上的数据。POST 用来新增。这是约定。浏览器地址栏、缓存、日志也更常看到 GET。不要用 GET 提交密码。",
        packet: "GET  /users      查列表\nPOST /users      新增一个用户",
        q: "新增用户应该用？",
        options: ["GET /users", "POST /users", "GET /createUser"],
        answer: 1,
        explain: "REST 习惯路径用名词复数。动作靠方法表达，不要做成 /createUser 这种动词路径。"
      },
      {
        title: "PUT 和 PATCH",
        why: "PUT 常常表示「整份替换」。PATCH 表示「只改一部分」。改一个用户的邮箱，更常见的是 PATCH。如果面试官不抠细节，你说明「局部用 PATCH、整份用 PUT」即可。",
        packet: "PUT   /users/1   整份用户数据换掉\nPATCH /users/1   只改 email",
        q: "只改邮箱，更贴切的是？",
        options: ["PUT，因为 PUT 更快", "PATCH，因为它表示局部修改", "GET，因为只改一个字段"],
        answer: 1,
        explain: "面试可以说：PUT 偏整体替换，PATCH 偏局部修改。项目里要和同事约定清楚，不要混用。"
      },
      {
        title: "状态码：成功",
        why: "2xx 表示成功。200 是通用成功。201 表示「创建了新东西」，新增用户最适合。204 表示成功但没响应体，删除有时会用。",
        packet: "200 OK          查询成功\n201 Created     新增成功\n204 No Content  删除成功且不返回身体",
        q: "新增成功为什么常用 201？",
        options: ["201 比较快", "它明确表示创建了新资源", "浏览器只认识 201"],
        answer: 1,
        explain: "面试可以说：状态码是前后端共同语言。新增 201，查询 200，比全部返回 200 更清楚。"
      },
      {
        title: "状态码：客户端错还是服务器错",
        why: "4xx 是调用方的问题：参数错、没登录、没权限、找不到、冲突。5xx 是服务器自己出问题：代码异常、数据库挂了。前端看到 500，不要先骂用户填错。",
        packet: "400 参数/业务不合法\n401 没登录\n403 登录了但没权限\n404 没有这个资源\n409 冲突，例如邮箱占用\n422 格式/类型过不了\n500 服务器内部错误",
        q: "年龄写成「十八」被 Pydantic 拦住，常见状态码？",
        options: ["500", "201", "422（类型/格式不对）"],
        answer: 2,
        explain: "面试可以说：形状不对 422，业务规则不对 400，邮箱占用 409，没登录 401，没权限 403，找不到 404，代码炸了 500。"
      },
      {
        title: "401 和 403",
        why: "401：我还不认识你，去登录。403：我认识你，但你不能做这件事。别混。前端「没 Token」是 401；普通员工删管理员账号是 403。",
        packet: "没带 Token → 401\n带了 Token 但角色不够 → 403",
        q: "已登录的普通用户去调「删除所有用户」接口，更合适的是？",
        options: ["401", "403", "201"],
        answer: 1,
        explain: "面试可以说：401 未认证，403 已认证但无权限。权限必须后端校验，不能只靠前端藏按钮。"
      },
      {
        title: "幂等",
        why: "幂等的意思：同样的请求做一次和做十次，最终状态一样。GET 查列表应该幂等。删除一个已经不存在的用户，再删一次，结果仍是「没有这个人」。POST 新增通常不幂等：点十次可能建十个。防重复提交要用唯一约束或幂等键。",
        packet: "GET /users/1     查多次，还是那条\nPOST /users      点十次可能十个用户",
        q: "下面哪项通常应该做成幂等？",
        options: ["POST 新增", "GET 查询、PUT 替换、DELETE 删除", "所有请求都不该幂等"],
        answer: 1,
        explain: "面试可以说：GET/PUT/DELETE 应尽量幂等。POST 创建默认不幂等，要防重复得额外设计。"
      }
    ]
  },
  {
    id: "fastapi",
    title: "FastAPI 基础",
    blurb: "路由、Pydantic、异步、跨域、鉴权。对应你简历上的后端技能。",
    steps: [
      {
        title: "FastAPI 适合做什么",
        why: "它用来写 HTTP 接口。好处是：用类型做校验（Pydantic）、支持异步、能自动生成接口文档。公司要的是 REST 接口，不是让你手写 Web 框架。",
        packet: "@app.post(\"/users\")\ndef create_user(body: UserIn) -> UserOut:\n    ...",
        q: "FastAPI 相对更突出的一点？",
        options: [
          "不能写 REST，只能写页面",
          "类型校验、异步、自动 OpenAPI 文档比较完整",
          "它就是数据库"
        ],
        answer: 1,
        explain: "面试可以说：Flask 更轻更自由；FastAPI 校验、异步和文档更开箱即用。我用它做过请求校验和接口返回。"
      },
      {
        title: "路由",
        why: "装饰器上的方法和路径必须和前端完全一致。少一个 s、方法写成 GET，都会对不上。对不上就是 404 或进错函数。",
        packet: "前端 POST /api/users\n后端 @app.post(\"/api/users\")   才能接住",
        q: "前后端路径差一个字母，通常会怎样？",
        options: ["FastAPI 自动纠正", "404 或根本进错接口", "数据库会按表名猜测"],
        answer: 1,
        explain: "联调第一件事：看 Network 里真实的方法、路径、状态码。不要先改业务代码。"
      },
      {
        title: "Pydantic 和业务校验",
        why: "Pydantic 管形状：缺字段、类型不对，直接 422。业务规则是另一层：满不满 18 岁、邮箱是否已存在。两层都要。有前端检查也不能取消后端检查。",
        packet: "Pydantic：age 必须是 int\n业务：age >= 18\n数据库：email 唯一",
        q: "哪句分工是对的？",
        options: [
          "Pydantic 管类型和必填；年龄规则和唯一邮箱是业务/数据库",
          "Pydantic 会查数据库唯一约束",
          "有了前端检查，后端可以不再检查"
        ],
        answer: 0,
        explain: "这是新增链路的核心。面试把三层说清：形状、业务、数据库约束。"
      },
      {
        title: "什么时候用异步",
        why: "等数据库、等别人的 HTTP 接口时，异步有意义。如果用的库是阻塞的，只把 def 改成 async def 不会变快。不要为了听起来高级把所有函数都写成异步。",
        packet: "适合：await 数据库 / await httpx\n不适合：把同步阻塞库套一层 async 就以为加速了",
        q: "异步自动让任何代码都更快吗？",
        options: ["是，写了 async 就一定快", "否，主要收益在等待型 IO，而且调用的库也要支持", "只有 Windows 上有效"],
        answer: 1,
        explain: "面试可以说：我理解异步是为了等待时不占死工人。具体项目里要看驱动和库是否真异步。"
      },
      {
        title: "CORS 跨域",
        why: "浏览器规定：网页的来源（协议+域名+端口）和接口不一致时，要后端明确允许，否则浏览器会拦截。本地常见：页面 5173，接口 8000。生产环境不要写成允许所有来源。",
        packet: "页面 http://127.0.0.1:5173\n接口 http://127.0.0.1:8000\n这就是不同来源，需要 CORS",
        q: "CORS 是谁在限制？",
        options: ["数据库", "浏览器，为了安全；后端要声明允许谁访问", "Python 语法"],
        answer: 1,
        explain: "面试可以说：跨域是浏览器行为。后端配置允许的前端地址。curl 能通但网页不行，经常就是 CORS。"
      },
      {
        title: "登录态不能只靠前端",
        why: "按钮藏起来挡不住会改请求的人。正确做法：登录后发 Token；每次请求后端校验身份和权限。前端隐藏只是体验。",
        packet: "错误：v-if=\"isAdmin\" 就不调删除接口，以为安全了\n正确：后端还要验 Token 和角色",
        q: "为什么权限必须放后端？",
        options: [
          "因为前端代码用户能改、请求能伪造",
          "因为后端比较慢所以更安全",
          "因为 Nginx 看不懂 Token"
        ],
        answer: 0,
        explain: "面试可以说：鉴权在服务端。前端只负责展示。防重复提交也一样，不能只靠按钮变灰。"
      },
      {
        title: "接口挂了先看哪",
        why: "不要一上来改代码。先看浏览器 Network：地址、方法、参数、状态码、响应。再看 FastAPI 终端日志，确认请求到没到、死在哪一步。最后才查数据库和环境变量。",
        packet: "1) Network\n2) 后端日志\n3) 数据库 / 环境变量 / 第三方",
        q: "联调失败时，第一步最该看？",
        options: ["先重写整个项目", "浏览器 Network 里这次请求的真实内容", "先重启电脑"],
        answer: 1,
        explain: "面试可以说：我按请求链路查：浏览器 → 后端日志 → 数据库。这比随机改代码快。"
      }
    ]
  },
  {
    id: "js",
    title: "HTML / CSS / JavaScript",
    blurb: "岗位偏前端。先分清三层，再补数组、异步请求和报错。",
    steps: [
      {
        title: "三层各管什么",
        why: "HTML 是结构：标题、按钮、输入框。CSS 是样子：大小、颜色、排版。JavaScript 是行为：点击、发请求、改数据。Vue 是在 JS 之上，帮你按组件和数据来更新界面。",
        packet: "HTML 骨架\nCSS 装修\nJS 让它动\nVue 有组织地管理页面",
        q: "点击按钮后向后端发请求，主要是谁的工作？",
        options: ["只靠 CSS", "JavaScript（或 Vue 里的 JS）", "只靠 HTML 标签名"],
        answer: 1,
        explain: "面试可以说：我能写基础页面结构、样式和请求。复杂工程化和性能优化还在补。"
      },
      {
        title: "let 和 const",
        why: "优先 const：这个名字不会再指向别的值。需要重新赋值再用 let。几乎不要用 var。const 的对象内部字段其实还能改，它锁的是变量指向，不是对象内部永远冻住。",
        packet: "const users = []\nusers.push(one)   # 可以，users 还是那个数组\nusers = []        # 不行，不能换指向",
        q: "一般情况下更推荐？",
        options: ["一律 var", "能用 const 就用 const，要重新赋值再用 let", "只用 let，永远不用 const"],
        answer: 1,
        explain: "面试可以说：const 防意外换引用。需要计数器那种再变的值才用 let。"
      },
      {
        title: "数组常用方法",
        why: "map：每个变成另一个，得到新数组。filter：留下符合条件的。find：找第一个。forEach：只做事不强调返回。面试常问 map 和 filter 的区别。",
        packet: "[1,2,3].map(x => x * 2)      → [2,4,6]\n[1,2,3].filter(x => x > 1)  → [2,3]",
        q: "要从用户列表里只留下未满 18 岁的人，更合适的是？",
        options: ["map", "filter", "把数组写成字符串再拆"],
        answer: 1,
        explain: "map 改变每一项的形态；filter 做筛选。不要用 map 当 filter 用。"
      },
      {
        title: "Promise 和 async/await",
        why: "网络请求不是立刻有结果。Promise 表示「将来才完成」。async/await 让这段等待写起来像同步，但页面不会整页卡死。失败要用 try/catch 接住，给用户提示。",
        packet: "async function load() {\n  try {\n    const res = await axios.get(\"/users\")\n    users.value = res.data\n  } catch (e) {\n    error.value = \"加载失败\"\n  }\n}",
        q: "await 一个请求时，整个网页会冻住不能点吗？",
        options: [
          "会，所以不能用 await",
          "不会冻住整个页面；它等的是这一次请求，同时浏览器还能画界面",
          "await 会自动重试十次"
        ],
        answer: 1,
        explain: "面试可以说：异步让等待网络时页面仍可响应。我用 try/catch 处理失败提示。"
      },
      {
        title: "JSON",
        why: "JSON 是前后端交换数据最常见的文本格式，长得像字典和列表。Content-Type 常写成 application/json。Python 的 dict、JS 的对象，和它很像，但细节不完全相同。",
        packet: "{\"name\": \"张三\", \"age\": 20}",
        q: "接口里最常见的数据交换格式是？",
        options: ["Word 文档", "JSON", "只能用 Excel"],
        answer: 1,
        explain: "面试可以说：请求体和响应体常用 JSON。字段名必须和后端约定一致，name 和 username 混用会联调失败。"
      },
      {
        title: "为什么数据不写死在页面里",
        why: "写死只能给你自己看。真实名单在服务器。页面负责展示这一次查到的结果。多人同时改用户时，大家看到的才是同一份数据。",
        packet: "错误：HTML 里写死三个用户\n正确：打开页面 → 请求 GET /users → 再渲染",
        q: "列表数据应该从哪来？",
        options: ["后端接口返回", "写死在 HTML 注释里", "从 CSS 颜色值里读"],
        answer: 0,
        explain: "这就是前后端分离：页面是壳，数据走接口。"
      },
      {
        title: "错误提示",
        why: "请求失败时，空白或转圈转不停都会让人以为坏了。要有 loading、成功结果、失败原因、空列表提示。finally 里关掉 loading，避免一直转。",
        packet: "loading = true\ntry { ... }\ncatch { 显示错误 }\nfinally { loading = false }",
        q: "无论成功失败都应该做的一件事？",
        options: ["关掉 loading", "把错误吞掉当成功", "刷新整个网站域名"],
        answer: 0,
        explain: "面试可以说：我会处理加载中、空数据、失败提示，而不是只做成功那一条路。"
      },
      {
        title: "联调最常见的坑",
        why: "地址或端口错、CORS、字段名不一致、没带 Token、没处理错误状态码。出现「我本地是好的」时，把 Network 截图和后端日志一起看。",
        packet: "前端 userName  vs  后端 username\n一个大写一个小写 → 对不上",
        q: "前端能收到 200 但页面没数据，很常见的原因？",
        options: [
          "字段名和页面用的不一致，或者数据在 data 里又包了一层",
          "Python 不能返回 JSON",
          "必须改成 GET 才能显示"
        ],
        answer: 0,
        explain: "面试可以说：先看响应 JSON 真实结构，再对字段。不要猜。"
      }
    ]
  },
  {
    id: "vue-basic",
    title: "Vue 核心概念",
    blurb: "组件、数据驱动、props、emit。偏前端岗几乎必问。",
    steps: [
      {
        title: "组件",
        why: "组件就是把页面拆成可复用的小块：表格一行、弹窗、分页。父组件拼页面，子组件管一小块。不要一个文件里堆所有 HTML。",
        packet: "UserList 里用很多个 UserRow",
        q: "组件主要是为了什么？",
        options: ["让数据库更快", "把界面拆成可复用、好维护的小块", "代替 HTTP"],
        answer: 1,
        explain: "面试可以说：我按列表、表单、弹窗拆组件。复杂抽象还在学，但这个思路是对的。"
      },
      {
        title: "响应式数据",
        why: "Vue 的数据不是普通变量。值变了，用到它的界面会跟着变。这就是「数据驱动视图」。列表 users 一更新，v-for 就会重画。",
        packet: "users 从 [] 变成 3 个人 → 页面自动出现 3 行",
        q: "为什么改了 users，列表会自己更新？",
        options: [
          "浏览器每秒刷新整个网站",
          "Vue 把数据做成响应式，变化后更新用到它的界面",
          "数据库会推送 HTML"
        ],
        answer: 1,
        explain: "面试可以说：我把列表、loading、错误信息放在响应式数据里，而不是直接操作一堆 DOM。"
      },
      {
        title: "props 往下",
        why: "父到子用 props。子组件把 props 当只读。想改名字，通知父亲去改。这叫单向数据流，好排查。",
        packet: "<UserRow :user=\"item\" />",
        q: "子组件直接改 props 会怎样？",
        options: ["官方推荐", "违反单向数据流，状态容易乱", "会自动写回数据库"],
        answer: 1,
        explain: "数据往下，事件往上。这是 Vue 必答题。"
      },
      {
        title: "emit 往上",
        why: "子组件不能偷偷删父亲手里的列表。它只能 emit：告诉父亲「用户点了删除」。父亲调接口，再更新列表。",
        packet: "子：emit('deleted', id)\n父：调 DELETE，再拉列表",
        q: "删除按钮在子组件里，真正发删除请求的通常是谁？",
        options: ["子组件自己偷偷改 props 就行", "父组件（或专门的数据层），因为列表数据在它这边", "Nginx"],
        answer: 1,
        explain: "面试可以说：子组件负责这一行的展示和点击，数据的增删在父组件或统一的接口层。"
      },
      {
        title: "computed 和 watch",
        why: "computed：由别的数据算出一个值，还有缓存，比如列表长度。watch：值变了之后去做一件事，比如搜索词变了就重新请求。别用 watch 去算一个能 computed 的值。",
        packet: "computed：total = users.length\nwatch：keyword 变化 → 再请求搜索接口",
        q: "显示「共 N 位用户」，更合适的是？",
        options: ["watch 每次手改一个数字", "computed 根据列表长度计算", "写死在 CSS 里"],
        answer: 1,
        explain: "面试原话：computed 算值；watch 做副作用（请求、存本地）。"
      },
      {
        title: "v-if 和 v-show",
        why: "v-if 是没有就销毁、有就创建。v-show 只是用 CSS 藏起来。频繁开关用 v-show 更合适。权限上不该存在的按钮，用 v-if 更合适。",
        packet: "偶尔出现的弹窗可以用 v-if\n频繁切换的小提示可以用 v-show",
        q: "一个提示一秒钟闪好多次，更合适？",
        options: ["v-show", "每次都 v-if 销毁重建通常更重", "必须同时写两个"],
        answer: 0,
        explain: "面试可以说：v-if 管「在不在」，v-show 管「看不看得见」。"
      },
      {
        title: "列表的 key",
        why: "v-for 必须给每项一个稳定 key。用数据库 id，不要用数组下标。下标在删除、排序后会乱，Vue 可能复用错那一行。",
        packet: "<div v-for=\"user in users\" :key=\"user.id\">",
        q: "为什么不推荐 :key=\"index\"？",
        options: [
          "下标会变，Vue 可能把错误的行复用到另一条数据上",
          "index 是非法关键字",
          "有了 index 就不能发请求"
        ],
        answer: 0,
        explain: "面试可以说：key 让 Vue 认出每一项是谁。用业务 id。"
      },
      {
        title: "onMounted",
        why: "组件刚出现在页面上时，适合拉一次列表。不要在脚本一加载、组件还没准备好时就乱请求。路由切到这个页，也会再走挂载。",
        packet: "onMounted(() => loadUsers())",
        q: "用户列表页第一次该在什么时机请求数据？",
        options: ["页面组件挂载完成后", "写在 CSS 文件里", "等用户猜到按哪个隐藏键"],
        answer: 0,
        explain: "面试可以说：进入页面 onMounted 拉数；提交后再拉或本地更新，保持和服务器一致。"
      }
    ]
  },
  {
    id: "sql-basic",
    title: "数据库与 SQL",
    blurb: "表、主键、关联、索引、事务。用「查每个用户订单数」把概念钉住。",
    steps: [
      {
        title: "为什么需要数据库",
        why: "程序重启，内存里的变量就没了。数据库把用户、订单长期存下来，还能多人同时改、按条件查。Excel 不是给网站高并发用的。",
        packet: "页面只是临时展示\n用户表长期存在 PostgreSQL / MySQL 里",
        q: "用户注册信息应该放哪？",
        options: ["只放在前端变量里", "数据库表里", "只放在 CSS 注释"],
        answer: 1,
        explain: "面试可以说：数据库负责持久化。前端刷新或换电脑，数据还在。"
      },
      {
        title: "表、行、列、主键",
        why: "表是一类数据。行是一条。列是字段。主键唯一标识一行，常用自增 id 或 UUID。没有主键，改和删都会很危险。",
        packet: "users 表\nid(主键) | name | email",
        q: "主键的作用？",
        options: ["让页面变好看", "唯一标识一行记录", "代替所有索引"],
        answer: 1,
        explain: "面试可以说：主键标识这一行。别的表要用外键指向它。"
      },
      {
        title: "外键",
        why: "订单属于用户。orders.user_id 指向 users.id。这就是外键。它表达「谁属于谁」，也避免出现「属于一个不存在的用户」的订单。",
        packet: "users.id  ←  orders.user_id",
        q: "订单表里的 user_id 通常是？",
        options: ["装饰用的随机数", "指向用户表主键的外键", "CSS 颜色值"],
        answer: 1,
        explain: "JOIN 时就要用这层关系：o.user_id = u.id，不是 o.id = u.id。"
      },
      {
        title: "INNER JOIN 和 LEFT JOIN",
        why: "INNER 只留两边都匹配的。LEFT 留左表全部，右边没有就空。问「每个用户的订单数」时，没下过单的人也要出现，必须 LEFT JOIN。",
        packet: "左表 users，右表 orders\nLEFT JOIN：李四没订单，仍出现，订单数 0",
        q: "要保留没有订单的用户，应该？",
        options: ["INNER JOIN", "LEFT JOIN 用户表", "把没订单的用户删掉"],
        answer: 1,
        explain: "这是高频题。先说结果长什么样，再选 JOIN 类型。"
      },
      {
        title: "GROUP BY 和 COUNT",
        why: "JOIN 完一个用户可能多行订单。GROUP BY 用户，把多行收成一行。LEFT JOIN 后要用 COUNT(订单id)，不要 COUNT(*)，否则没订单的人会被算成 1。",
        packet: "SELECT u.name, COUNT(o.id)\nGROUP BY u.id, u.name",
        q: "LEFT JOIN 后统计订单数，为什么 COUNT(o.id) 而不是 COUNT(*)？",
        options: [
          "没订单时仍有一行用户，COUNT(*) 会变成 1，COUNT(o.id) 才是 0",
          "两种永远一样",
          "COUNT(*) 语法错误"
        ],
        answer: 0,
        explain: "面试官很爱问这个坑。你已经在链路上见过，这里再钉一次。"
      },
      {
        title: "索引",
        why: "索引像书的目录。orders.user_id 常用来按用户找订单，适合建索引。不是列越多越好：占空间，写入还要维护。对索引列做函数、前置模糊查询，可能用不上索引。",
        packet: "CREATE INDEX idx_orders_user_id ON orders(user_id);",
        q: "索引越多越好吗？",
        options: ["是，每个列都建", "不是，占空间而且拖慢写入，只给常筛选、常 JOIN 的列建", "没有索引就不能 SELECT"],
        answer: 1,
        explain: "面试可以说：索引加速读、略微拖慢写。用 EXPLAIN 看有没有真的用上。"
      },
      {
        title: "事务 ACID",
        why: "原子性：多步要么全成要么全撤。一致性：规则始终被满足。隔离性：并发时别看到不该看的中间态。持久性：提交后重启还在。转账、用户+账户一起创建，必须用事务。",
        packet: "BEGIN\n  插入用户\n  插入账户\nCOMMIT\n失败则 ROLLBACK",
        q: "事务的原子性是指？",
        options: [
          "操作很快",
          "多步要么全部成功，要么全部回滚",
          "只能有一张表"
        ],
        answer: 1,
        explain: "面试可以说：我理解事务是为了避免只成功一半。单表插入包事务也无害。"
      },
      {
        title: "N+1 查询",
        why: "先查 100 个用户，再在循环里每人查一次订单，就是 1+100 次。数据库来回太多次。应该 JOIN 一次或批量查。这叫 N+1，面试常问。",
        packet: "坏：for user in users: 再 SELECT 他的订单\n好：一次 JOIN 或 WHERE user_id IN (...)",
        q: "N+1 为什么慢？",
        options: [
          "循环里重复访问数据库，次数随用户数增加",
          "SQL 关键字写错了",
          "浏览器不能显示超过 1 行"
        ],
        answer: 0,
        explain: "面试可以说：能批量就批量。先保证结果正确，再看次数和 EXPLAIN。"
      }
    ]
  },
  {
    id: "ops",
    title: "Linux、Git、部署",
    blurb: "从 127.0.0.1 到别人能打开。Nginx、Uvicorn、Docker、Git 各管一段。",
    steps: [
      {
        title: "127.0.0.1",
        why: "这是「这台电脑自己」。你本地跑通，只证明你的代码能跑。同事的浏览器打你的 127.0.0.1，进的是他的电脑，不是你的。",
        packet: "uvicorn --host 127.0.0.1 --port 8000",
        q: "同事打不开你的 127.0.0.1:8000，因为？",
        options: ["端口被禁用", "那是你机器自己的地址", "必须先买域名才能本地运行"],
        answer: 1,
        explain: "面试可以说：本地验证用回环地址；上线要放到有公网或内网可达地址的服务器。"
      },
      {
        title: "Nginx 和 Uvicorn",
        why: "Uvicorn 跑 Python 应用。Nginx 当大门：HTTPS、静态文件、把请求转给内部的 Uvicorn。顺序：浏览器 → Nginx → Uvicorn → FastAPI → 数据库。",
        packet: "用户 → Nginx:443 → Uvicorn:8000 → FastAPI",
        q: "谁更适合当公网大门？",
        options: ["Uvicorn 直接对全世界", "Nginx 反代到内部 Uvicorn", "数据库直接对外"],
        answer: 1,
        explain: "面试可以说：Nginx 管入口和静态资源，Uvicorn 管 Python 进程。两者不是重复。"
      },
      {
        title: "环境变量",
        why: "密钥、数据库地址不要写进代码、不要提交 Git。放在环境变量或 .env（且 .env 加入忽略名单）。换一台机器只改配置，不改代码。",
        packet: ".env 里放 DEEPSEEK_API_KEY\n代码只读 os.getenv",
        q: "API 密钥应该？",
        options: ["写在 GitHub 公开仓库里", "放环境变量或受保护配置，不进代码仓库", "写在前端 JS 里给所有人看"],
        answer: 1,
        explain: "面试可以说：配置与代码分离。泄露密钥要立刻作废重签。"
      },
      {
        title: "Docker",
        why: "镜像是只读模板，容器是跑起来的实例。Dockerfile 描述怎么做镜像。Volume 把数据放容器外，避免一删容器数据没了。「在我电脑能跑」靠它减少环境差。",
        packet: "镜像 = 菜谱和食材包\n容器 = 按菜谱做出来正在烧的那道菜",
        q: "Docker 主要解决？",
        options: ["运行环境不一致", "让 SQL 不用 JOIN", "代替 Git"],
        answer: 0,
        explain: "面试可以说：镜像保证依赖一致。数据用 Volume 持久化。我理解概念，生产编排经验有限，会诚实说。"
      },
      {
        title: "Git 最小闭环",
        why: "status 看改了什么。add 选要提交的。commit 留下说明。pull 先拿别人的。push 上传。分支把新功能和稳定主线隔开。冲突是同一处被两人改，要人工合并再测。",
        packet: "改代码 → git add → git commit → git pull → git push",
        q: "commit 是在做什么？",
        options: ["立刻部署上线", "留下一条有说明的本地历史记录", "删除远端仓库"],
        answer: 1,
        explain: "面试可以说：我能独立完成日常提交和拉推。冲突会先看两边意图再测。"
      },
      {
        title: "网站打不开怎么查",
        why: "按链路：域名解析 → Nginx 活着吗 → 后端进程和端口 → 本机 curl → 后端日志 → 数据库连接 → 环境变量 → 防火墙和证书。不要第一步就重装系统。",
        packet: "浏览器 → DNS → Nginx → Uvicorn → 应用 → 数据库",
        q: "排查线上打不开，比较合理的顺序？",
        options: [
          "先从入口一路往后：域名、Nginx、后端端口、日志、数据库",
          "先重写全部前端",
          "先删数据库"
        ],
        answer: 0,
        explain: "和查接口失败一样：顺着请求走，每一步验证「到了没有」。"
      },
      {
        title: "Linux 看一眼",
        why: "不必成为运维。但要知道：ls/cd/pwd 看文件，ps/ss 看进程和端口，df/free 看磁盘内存，docker logs 看容器，curl 测接口。面试问「你会 Linux 吗」，就举这些。",
        packet: "ss 看 8000 有没有人守着\ncurl http://127.0.0.1:8000/users",
        q: "怀疑后端没起来，本机可以先？",
        options: ["看端口和进程，再用 curl 打接口", "先格式化磁盘", "改 Vue 组件名"],
        answer: 0,
        explain: "面试可以说：我会用基础命令确认进程、端口和日志。复杂排障会查文档、请教同事。"
      }
    ]
  },
  {
    id: "coding",
    title: "现场写题习惯",
    blurb: "面试官看的是确认题意、边界和沟通，不是背最优算法。",
    steps: [
      {
        title: "先确认输入输出",
        why: "空列表返回什么？重复怎么算？输出要排序吗？不问就写，容易整道题作废。先举一个小例子对一对。",
        packet: "题：出现次数最多的元素\n先问：空数组？并列最多？",
        q: "拿到题第一步？",
        options: ["立刻写最复杂的优化", "确认输入、输出和空数据怎么处理", "先说自己不会并沉默"],
        answer: 1,
        explain: "面试可以说：我先确认题意和小例子，再写能跑的版本。"
      },
      {
        title: "词频和去重",
        why: "词频：字典计数，扫一遍。去重且保持顺序：集合记「见过没」，列表存结果。只把 set 转回列表，顺序可能丢。",
        packet: "见过 = set()\n结果 = []\n没见过就放进结果，并记入 set",
        q: "保持顺序去重，为什么不能只 return set(arr)？",
        options: ["集合不保证原来的顺序", "集合不能装数字", "set 会连数据库一起删"],
        answer: 0,
        explain: "两道高频小题：字典计数；set+list 保序去重。准备各讲 30 秒。"
      },
      {
        title: "按用户分组",
        why: "字典的 key 是用户 id，value 是订单列表。缺 id 的订单要先说怎么处理：跳过还是报错。这和 SQL GROUP BY 是同一类问题。",
        packet: "groups.setdefault(user_id, []).append(order)",
        q: "把订单按用户归堆，最直接的结构是？",
        options: ["用户 id → 该用户的订单列表", "只用一个大字符串拼接", "每个订单一张新表，不要主键"],
        answer: 0,
        explain: "面试可以说：我用字典分组。再补一句缺字段怎么办。"
      },
      {
        title: "卡住时怎么说话",
        why: "沉默乱写比不过边写边说。库名记不清，就用基础循环先保证正确。发现漏了空数据，主动补。面试官要的是可合作的人。",
        packet: "「我先写能跑的版本，再看要不要优化。」",
        q: "函数名一时想不起来，比较好的做法？",
        options: [
          "空白盯着直到时间结束",
          "先用基础写法保证逻辑正确，并说明库名不确定",
          "编一个肯定不存在的库并坚持用"
        ],
        answer: 1,
        explain: "准备三句：先可运行；库名不确定用基础循环；漏了边界现在补。"
      },
      {
        title: "写完要测",
        why: "正常数据、空数据、重复、极端值。SQL 题要自己带一个「没订单的用户」。接口题要说重复邮箱返回什么。",
        packet: "正常 / 空 / 重复 / 极端",
        q: "写完代码后应该？",
        options: ["立刻离开", "用几类边界数据走一遍", "把变量全改成单字母再交"],
        answer: 1,
        explain: "主动测试会加分。即使题没写完，把测试想法说出来也有用。"
      }
    ]
  }
];

window.LEARN_FAQ = [
  {
    id: "hr",
    title: "HR 与自我介绍",
    blurb: "为什么投、优缺点、薪资、不会时怎么说。先选对方向，再记口头稿。",
    steps: [
      {
        title: "为什么投这个岗位",
        why: "他们要 Python 全栈、偏前端。你的真实匹配是：接口和流程更熟，前端能做基础页面和联调，想在产品里把前后端补全，也对公司 AI 项目感兴趣。不要说「什么都行」「只是离家近」。",
        packet: "建议说：Python 和接口和经历匹配；前端正在补，能做基础联调；想积累完整上线经验，也关注公司 AI 方向。",
        q: "哪句更合适？",
        options: [
          "什么岗位都行，你们招人我就来",
          "接口和 Python 匹配，前端能做基础联调并在补强，想做完整产品也关心 AI 项目",
          "我只投 AI 岗，这个全栈我完全不感兴趣"
        ],
        answer: 1,
        explain: "不要把岗位说成 coaster。也不要假装自己已经是前端专家。"
      },
      {
        title: "优势怎么说",
        why: "优势要能举例子：拆流程、写 Python 接口和脚本、从日志和输入输出定位。空话「学习能力强」没有证据。",
        packet: "可以说：能把流水线拆成步骤；会写接口和自动化；出问题先看日志和输入输出。",
        q: "更有说服力的优势是？",
        options: [
          "我性格好、学习能力强（到此为止）",
          "能拆业务流程、写接口和脚本，并按日志定位",
          "我会所有框架"
        ],
        answer: 1,
        explain: "每个优点后面都要能接「比如在某某项目里……」。"
      },
      {
        title: "不足怎么说",
        why: "要真实且可补：前端工程化少于后端，但能做基础页面和联调，正在补组件化和状态。不要说「没有缺点」，也不要说「前端完全不会」。",
        packet: "不足：前端工程化经验较少。\n补救：能做列表表单联调，正在系统补 Vue。",
        q: "更合适的不足表述？",
        options: [
          "我没有缺点",
          "前端工程化少于后端，但能做基础页面和联调，正在补",
          "我完全不会前端，希望入职再学 HTML"
        ],
        answer: 1,
        explain: "承认短板 + 已有能力边界 + 正在做什么。这是成熟答法。"
      },
      {
        title: "期望薪资",
        why: "你和 HR 已说过八到九千。岗位条是七到十千。现场不要突然加到明显高于聊天记录。可以说结合岗位范围，具体看职责和试用期。",
        packet: "期望八到九千，可按职责、试用期和整体待遇沟通。",
        q: "现场薪资怎么说更稳？",
        options: [
          "临时报到远高于聊天记录的数字",
          "按之前沟通的八到九千，结合职责和试用期谈",
          "说越低越好，请他们随便定"
        ],
        answer: 1,
        explain: "和聊天记录保持一致。问清试用期比例和社保时间。"
      },
      {
        title: "不会的题",
        why: "先说会的部分，再划清边界。不要编。不要空白。可以说：只了解基本概念；某块是同事负责但我知道怎么联调；不确定的细节会查日志和文档再小实验。",
        packet: "「这个我只了解基本概念，我先说我理解的部分。」",
        q: "不会时最差的做法？",
        options: [
          "先讲会的，再说明不确定之处",
          "编一个听起来很厉害但自己没做过的实现",
          "说明会查日志和文档"
        ],
        answer: 1,
        explain: "诚实加方法，比装懂更安全。装懂会被追问到穿。"
      },
      {
        title: "为什么录用你",
        why: "应届但有真实流程；Python 和接口能较快投入；AI 经历是加分不是冒充资深算法。不要说「因为我便宜、能无条件加班」。",
        packet: "有真实项目经验，能较快做接口和联调，也愿意补前端，并能带来一点 AI 应用视角。",
        q: "更合适的理由？",
        options: [
          "我工资低所以更合适",
          "有真实流程和接口经验，能投入全栈并补前端，AI 经历是额外价值",
          "两年后我就是架构师"
        ],
        answer: 1,
        explain: "把「能交付什么」说清楚，比喊口号强。"
      }
    ]
  },
  {
    id: "faq-api",
    title: "接口高频问答",
    blurb: "FastAPI、REST、跨域、鉴权、排错。尽量用新增用户当例子。",
    steps: [
      {
        title: "用一个例子讲 REST",
        why: "别背定义。用 users 资源把 GET/POST/PATCH/DELETE 串起来。路径用名词，动作用方法。",
        packet: "GET 列表 / GET 一个 / POST 新增 / PATCH 改 / DELETE 删",
        q: "哪句更像 REST 习惯？",
        options: [
          "路径全是 /doGetUser /doSave",
          "资源用 /users，用 HTTP 方法表示动作",
          "所有操作都用 GET，靠参数 action=delete"
        ],
        answer: 1,
        explain: "口头：我按资源设计。新增用户就是 POST /users，成功 201。"
      },
      {
        title: "FastAPI 和 Flask",
        why: "Flask 轻、自由度高。FastAPI 类型校验、异步、OpenAPI 更完整。不要贬低 Flask，说场景差异。",
        packet: "要快速接口和文档、类型校验 → FastAPI 很合适",
        q: "更公允的对比？",
        options: [
          "Flask 已经过时不能用",
          "Flask 更轻；FastAPI 校验、异步和文档更开箱即用",
          "两者没有区别"
        ],
        answer: 1,
        explain: "结合你做过 FastAPI 接口来说，不要假装两种都精通到源码级。"
      },
      {
        title: "CORS 现场怎么答",
        why: "先说浏览器限制不同来源。再说本地端口不同就会碰到。最后说生产要写明白来源，不要 *。",
        packet: "页面端口 ≠ 接口端口 → 浏览器拦截 → 后端放行指定来源",
        q: "curl 通、浏览器不通，优先怀疑？",
        options: ["硬盘坏了", "CORS 或前端取字段取错", "Python 版本必须降到 2.7"],
        answer: 1,
        explain: "先看浏览器控制台有没有跨域报错，再看 Network。"
      },
      {
        title: "Token 放哪",
        why: "常见：登录成功后发 Token，之后请求放在 Authorization 头。后端每次校验。前端存 Token 要注意别泄露。权限仍以服务端为准。",
        packet: "Authorization: Bearer <token>",
        q: "只在前端隐藏「删除」按钮够不够？",
        options: ["够，别人看不到就不会调接口", "不够，后端必须校验身份和权限", "够，因为 HTTP 不能伪造"],
        answer: 1,
        explain: "这题几乎必出。答案必须落到服务端校验。"
      },
      {
        title: "重复提交",
        why: "按钮变灰只是体验。真正防的是：数据库唯一约束、业务上检查已存在、或客户端带幂等键。新增用户的邮箱唯一就是一种。",
        packet: "邮箱 UNIQUE + 后端先查再插 + 冲突返回 409",
        q: "防重复创建用户，关键靠？",
        options: ["只靠按钮变灰", "后端检查 + 数据库唯一约束", "只靠用户自觉"],
        answer: 1,
        explain: "把 409 和唯一索引一起说，面试官会觉得你做过接口。"
      },
      {
        title: "4xx 怎么给前端",
        why: "返回可理解的信息：哪一字段错、为什么。不要只回 Internal Error。也不要把堆栈和密钥返回给浏览器。",
        packet: "{\"detail\": \"邮箱已被占用\"}",
        q: "参数错误时，比较好的响应？",
        options: [
          "500 加一长串堆栈",
          "4xx + 人能看懂的字段说明",
          "200 但 body 里写失败"
        ],
        answer: 1,
        explain: "成功就真成功。失败用状态码表达。不要 200 里藏 error。"
      }
    ]
  },
  {
    id: "faq-fe",
    title: "前端高频问答",
    blurb: "computed/watch、key、组件通信、深度不够时怎么说。",
    steps: [
      {
        title: "computed 和 watch（口播）",
        why: "这是 Vue 第一高频。computed 是「算一个值，能缓存」。watch 是「变了去做一件事」。列表总数用 computed；搜索词变化去请求用 watch。",
        packet: "算值 → computed\n副作用 → watch",
        q: "搜索框停止输入后去请求，更像？",
        options: ["computed", "watch（值变化后发请求）", "v-show"],
        answer: 1,
        explain: "口头两句就够。再各举一个你页面上的例子。"
      },
      {
        title: "组件通信（口播）",
        why: "父传子 props，子传父 emit。跨很多层再提 Pinia/事件总线，但你没做复杂状态管理就不要展开装熟。",
        packet: "props 下，emit 上",
        q: "列表在父、行在子，删除应？",
        options: ["子直接改 props 删掉那一行", "子 emit，父调接口并更新列表", "子自己再请求全量用户然后不告诉父"],
        answer: 1,
        explain: "把新增链路和列表页、行组件三件事串起来讲，就是完整前端故事。"
      },
      {
        title: "key 和 v-if",
        why: "key 用 id。v-if 销毁，v-show 隐藏。空状态和列表分开写，不要 v-for 和 v-if 糊在同一元素上搞晕自己。",
        packet: "v-if=\"!users.length\" 暂无数据\nv-else v-for 列表",
        q: "空列表时更好的界面？",
        options: ["空白什么都不显示", "明确的空状态提示", "用 404 页面冒充"],
        answer: 1,
        explain: "细节体现你做过页面：loading、空、错、有数据。"
      },
      {
        title: "被问前端很深时",
        why: "不要硬扛源码。可以说：能完成列表、表单、请求、联调，会看 Network 和控制台。复杂抽象、性能优化、大型状态管理经验少，正在补。然后把话拉回你做过的页面链路。",
        packet: "能力边界说清楚，立刻给一个你做过的例子。",
        q: "被问虚拟列表原理但你没做过，更好的是？",
        options: [
          "编一套原理坚持到底",
          "承认没做过，说明会从官方文档和现有列表页入手，并讲你实际做过的加载与更新",
          "说 Vue 不能做列表"
        ],
        answer: 1,
        explain: "偏前端岗会追问。诚实 + 你的列表提交删除链路，比假精通安全。"
      },
      {
        title: "Vue2 还是 Vue3",
        why: "HR 未必写清。你可以答：我按组合式 API / 选项式都能读懂文档；入职会按仓库实际版本走。反问他们用 Vue2 还是 3、有没有 TypeScript。",
        packet: "现场反问：团队 Vue 2 还是 3？是否 TS？",
        q: "版本不确定时？",
        options: [
          "说自己只精通某一个且拒绝另一个",
          "说明能读文档上手，并问清团队版本",
          "说框架不重要所以没学过"
        ],
        answer: 1,
        explain: "把问题抛回去，显得你在核实工作内容，不是只会背题。"
      }
    ]
  },
  {
    id: "faq-db",
    title: "数据库高频问答",
    blurb: "索引、事务、JOIN、慢查询。每题都给出口头一句。",
    steps: [
      {
        title: "索引口头定义",
        why: "像目录。给常出现在 WHERE、JOIN、ORDER BY 且区分度高的列建。用 EXPLAIN 验证，不凭感觉。",
        packet: "orders.user_id 上建索引，按用户查订单更快",
        q: "哪些列更适合索引？",
        options: [
          "所有列，包括很少用的备注",
          "经常筛选、关联、排序，且区分度较高的列",
          "只有主键以外都不能建"
        ],
        answer: 1,
        explain: "补一句副作用：占空间、拖慢写。这就完整了。"
      },
      {
        title: "事务口头定义",
        why: "用转账或「创建用户同时开账户」。强调要么一起成功要么一起回滚。再点四个字母里你最熟的原子性和持久性。",
        packet: "BEGIN … COMMIT / ROLLBACK",
        q: "转账扣 A 加 B，中途崩溃最怕什么？",
        options: ["只成功一半，所以要事务", "SQL 关键字太长", "前端没用 Vue"],
        answer: 0,
        explain: "ACID 四个字都能用白话各说一句最好。至少原子性要能举例子。"
      },
      {
        title: "LEFT JOIN 口头题",
        why: "先说结果表要有所有用户。再说没订单的人订单数是 0。然后 SQL：LEFT JOIN + COUNT(o.id) + GROUP BY。",
        packet: "用户名 | 订单数\n张三 2\n李四 0",
        q: "这道题选 INNER JOIN 会怎样？",
        options: ["李四会消失", "更快而且结果一样", "数据库会自动补 0"],
        answer: 0,
        explain: "现场若让你写，先画两行结果再写 SQL，不容易写错。"
      },
      {
        title: "慢查询怎么查",
        why: "先确认 SQL 结果对。再看时间。EXPLAIN 看有没有全表扫、有没有用索引。检查是不是循环里逐条查（N+1）。不要一上来就加十个索引。",
        packet: "正确 → 耗时 → 执行计划 → 是否 N+1 → 再考虑索引",
        q: "慢查询第一步？",
        options: ["先确认结果对不对，再看计划和耗时", "先删表", "先把所有列改成 TEXT"],
        answer: 0,
        explain: "有这一套顺序，比背优化清单像做过事。"
      },
      {
        title: "MySQL 和 PostgreSQL",
        why: "JD 两个都写了。可以说：都是关系型数据库，表、SQL、事务、索引一套通用；语法和部分类型有差异。你更熟哪边就说哪边，另一边能读文档上手。不要假装两个都调过源码。",
        packet: "通用：表、主键、JOIN、事务、索引\n差异：具体类型、部分函数、运维细节",
        q: "两个都不会装很熟时？",
        options: [
          "说自己闭眼能做内核开发",
          "强调关系型通用能力，并说明具体方言以项目为准",
          "说 SQL 已经过时"
        ],
        answer: 1,
        explain: "用「查用户订单数」证明你会 SQL，比争论哪个数据库更好有用。"
      }
    ]
  },
  {
    id: "faq-ops",
    title: "部署与 Git 高频",
    blurb: "Nginx/Uvicorn/Docker 分工，Git 冲突，线上打不开。",
    steps: [
      {
        title: "一口说出上线链路",
        why: "浏览器经域名和 HTTPS 到 Nginx，转到 Uvicorn 里的 FastAPI，FastAPI 访问数据库，JSON 回页面。Docker 用来让环境和代码一起走。",
        packet: "浏览器 → Nginx → Uvicorn → FastAPI → PostgreSQL",
        q: "这条链里 Nginx 的角色？",
        options: ["跑 Python 字节码", "公网入口、HTTPS、静态文件、反代到应用", "代替 Git"],
        answer: 1,
        explain: "把四个名字按顺序背熟。这是部署题的骨架。"
      },
      {
        title: "镜像和容器",
        why: "镜像是模板，容器是实例。删容器不等于删镜像。数据要放 Volume，否则容器一没数据没。",
        packet: "build 出镜像，run 出容器",
        q: "容器删了，数据库文件还在吗？",
        options: [
          "如果只写在容器里，可能没了；用 Volume 挂出来才稳",
          "Docker 会自动备份到 GitHub",
          "容器和镜像是同一个东西"
        ],
        answer: 0,
        explain: "面试常问。一句话：无状态进镜像，有状态进 Volume。"
      },
      {
        title: "Git 冲突",
        why: "两人改了同一段。Git 标出来。你要看两边想干什么，合成一份，跑一下再提交。不要盲目全收某一方。",
        packet: "<<<<<<< 我的\n=======\n对方的\n>>>>>>>",
        q: "遇到冲突应该？",
        options: ["随便选一边提交", "理解两边改动，合并后测试再提交", "删除整个仓库"],
        answer: 1,
        explain: "说你做过或能按这个流程做。团队开发几乎必问。"
      },
      {
        title: "为什么要分支",
        why: "主线保持可上线。新功能在分支做，做完再合。避免半成品直接上生产。",
        packet: "main 稳定，feature/xxx 做新功能",
        q: "功能开发为什么不直接在主分支上改？",
        options: ["为了把半成品和稳定版本隔开", "Git 禁止在主分支 commit", "分支能让 SQL 更快"],
        answer: 0,
        explain: "结合「先拉再改再推」，就是日常协作。"
      },
      {
        title: "线上事故口述",
        why: "用排查顺序当答案。即使你没值过班，顺序对就说明你不慌。最后补：看日志，不猜。",
        packet: "DNS → Nginx → 端口进程 → curl → 日志 → 数据库 → 配置 → 证书防火墙",
        q: "用户说网站打不开，你先？",
        options: ["从自己电脑能不能打开、域名和入口服务查起", "先骂用户", "先把数据库 drop"],
        answer: 0,
        explain: "态度：先复现，再沿链路。这和查接口 500 是同一思维。"
      }
    ]
  },
  {
    id: "faq-proj",
    title: "项目与 TestPilot 怎么讲",
    blurb: "用同一套顺序讲项目。TestPilot 只能讲已完成的，不能把规划当成绩。",
    steps: [
      {
        title: "项目题七步",
        why: "背景、目标、流程、本人工作、难点、结果、反思。缺「我做了什么」和「怎么验证」最容易被打假。",
        packet: "谁的问题 → 输入输出 → 步骤 → 我写了哪 → 一次真实故障 → 数字怎么来 → 重做先改哪",
        q: "最不该只做哪件事？",
        options: ["只报框架名字和架构图", "讲自己写的模块和一次排障", "说明指标怎么算"],
        answer: 0,
        explain: "每个项目准备 90 秒按这七步说。数字必须能解释分子分母。"
      },
      {
        title: "访谈流水线怎么讲",
        why: "目标是英文访谈变中文成片。你串自动流程、处理时长、把部分时序拆到 Go、断点续传和失败回退。62/67、1 秒、1.25 秒、40 余项测试，要能说清怎么算。",
        packet: "不要只说「我做了 AI」。要说步骤、你写的部分、一个故障、一个数字。",
        q: "被问 62/67 时必须能说？",
        options: [
          "67 是什么片段、误差怎么定义、另外 5 段为什么不达标",
          "这是同事编的不用管",
          "数字越大越好所以不用解释"
        ],
        answer: 0,
        explain: "准备：为什么拆 Go、续传状态放哪、失败哪些重试哪些人工、测试各举正常/边界/失败一例。"
      },
      {
        title: "Agent 平台怎么讲",
        why: "你是功能与异常验证、定位和回归，不是声称自己写了 Agent 内核。用会话串话、停止失效、工具断网这些失败模式，体现你懂状态隔离和取消信号。",
        packet: "串话 → 会话要隔离\n停止失效 → 取消信号要传到服务端",
        q: "这段经历最稳妥的定位？",
        options: [
          "我独立设计了 Multi-Agent 框架",
          "我做功能与异常验证，能讲清失败模式和开发要注意什么",
          "我只点点点，什么原理都不知道"
        ],
        answer: 1,
        explain: "把测试经历翻译成开发意识，但不要改成「我是框架作者」。"
      },
      {
        title: "TestPilot 绝对不能怎样讲",
        why: "现在真实完成的是：FastAPI 页、DeepSeek、五篇本地资料、整文件 BM25。切块、向量库、LangGraph、React、PostgreSQL、CI、公网部署都还没有。规划不是成绩。",
        packet: "可以说：正在迭代的原型，目前是本地问答 + BM25。下一步才是切块和评测。",
        q: "哪句是诚实的？",
        options: [
          "已经完成向量库、LangGraph 和生产部署",
          "目前是本地检索问答原型，完整架构是目标不是现状",
          "Hit@5 已经 93%，来自公开榜"
        ],
        answer: 1,
        explain: "被追问就承认阶段。把「我会按链路把请求讲清楚」当成能力证明，而不是假装系统已经很大。"
      },
      {
        title: "失败故事格式",
        why: "现象 → 最初假设 → 证据（日志/输入输出/对照）→ 真因 → 修复 → 如何防止再发生。不要只说「反复调试好了」。",
        packet: "有证据的一次排障，比十个形容词强。",
        q: "失败故事里必须出现？",
        options: ["至少一种证据：日志、输入输出或对照实验", "只说熬夜了", "只说用了 ChatGPT"],
        answer: 0,
        explain: "访谈时长、会话串话、接口 422，都可以套这个格式。"
      },
      {
        title: "现场设计新增用户接口",
        why: "这是写题和口试的交界。按你已经会的链路说：校验、查重、事务、201/409/422，日志不打密码。这就是满分骨架。",
        packet: "路由 → Pydantic → 业务 → 事务插入 → 状态码 → 前端更新",
        q: "设计该接口时最不该漏的是？",
        options: [
          "校验、唯一约束、失败状态码和成功后的页面更新",
          "只写一个 print",
          "把密钥写进返回 JSON"
        ],
        answer: 0,
        explain: "你已经能完整讲这条。高频问答里再遇到，就按链路背一遍。"
      }
    ]
  }
];
