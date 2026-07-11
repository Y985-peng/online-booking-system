# 项目错误日志（ERR_LOG）

> 每次修复后记录错误原因与解决办法，后续修改前先查阅此文件避免重复犯错。

---

## 错误记录

---

### #1 — `NameError: name 'Notification' is not defined`

**时间**：2026-07-10

**触发条件**：在 `posts/serializers.py` 中新增 `NotificationSerializer`，其 `Meta.model = Notification` 引用了 `Notification` 模型，但没有在文件顶部导入。

**错误信息**：
```
File "posts/serializers.py", line 77, in Meta
    model = Notification
NameError: name 'Notification' is not defined
```

**根因**：在 `serializers.py` 顶部 `from .models import ...` 中漏写了 `Notification`。当时只导入了旧模型（`Post`, `PostLike`, `PostFavorite`, `PostComment`, `Follow`），新增的 `Notification` 模型没有加进 import 语句。

**解决办法**：将 `Notification` 加入导入：
```python
from .models import Post, PostLike, PostFavorite, PostComment, Follow, Notification
```

**预防**：新增模型后，检查所有引用该模型的文件是否都已补充 import。

---

### #2 — `CssSyntaxError: Unknown word |`

**时间**：2026-07-11

**触发条件**：在 `ChatConversation.vue` 中用 `sed` 命令替换 `text-align: center` 为 `text-align: left`，sed 命令语法错误导致文件中残留了 `*text-align: left;|` 这样的无效 CSS。

**错误信息**：
```
CssSyntaxError: [postcss] ...:22:45: Unknown word |
```

**根因**：`sed` 命令写错了，没有直接替换而是插入了一些占位符字符。后续没做语法校验就构建。

**解决办法**：清理文件中残留的 `*text-align: left;|` 之类垃圾字符。

**预防**：对所有 `.vue` 文件的 CSS 修改，优先用 Python 脚本（`content.replace()`）而不是 `sed`，因为 `.vue` 里的 CSS 和 HTML/JS 混杂，sed 容易破坏结构。

---

### #3 — `Unterminated string constant`

**时间**：2026-07-11

**触发条件**：在 `ServiceDetail.vue` 的 Python 脚本注入中，字符串 `'转发帖子:\n'` 中的 `\n` 被 Python 解释为真正的换行符写入了文件，导致 JavaScript 字符串跨行。

**错误信息**：
```
SyntaxError: [vue/compiler-sfc] Unterminated string constant. (104:19)
```

**根因**：Python 脚本里的 `content.replace(..., "const text = '转发帖子:\\n' + ...")` 中，`\\n` 在 Python 字符串字面量中表示一个反斜杠后跟 `n`，但实际写入文件后变成了字面量 `\n` 和 `'` 被放在了不同行。本质是 Python 字符串转义和 JavaScript 字符串转义混淆。

**解决办法**：改用 `'[转发] ' + ` 拼接，或使用 JavaScript 模板字符串 `` `转发帖子: ${...}` ``。

**预防**：Python 写 JS 代码时，换行符(`\n`)用 `\\n` 在 Python 字符串中表示，或在 Python 字符串中使用 raw string (`r'...'`)。更简单的方法是避免让 Python 处理含换行符的 JS 字符串。

---

### #4 — 帖子相关的后端字段/模型改动后未在部署时跑迁移

**时间**：多次

**触发条件**：新增了 `PostLike`、`PostFavorite`、`PostComment`、`Notification` 模型后，部署到 PythonAnywhere 时没有执行 `python manage.py migrate posts`。

**错误信息**：`no such table` 或 import 错误

**根因**：本地 `makemigrations` 生成了迁移文件，但服务器数据库没有应用这些迁移。

**解决办法**：部署步骤中加入：
```bash
python manage.py migrate posts
```

**预防**：每次修改模型后，把迁移命令写进部署步骤。部署流程统一维护在项目根目录 `DEPLOY.md` 中。

---

### #5 — 头像显示"我"而不是用户真实头像

**时间**：2026-07-11

**触发条件**：聊天页面 `ChatConversation.vue` 中用户自己的头像仅显示紫色背景"我"字，没有显示上传的真实头像。

**根因**：`userStore.userInfo?.avatar` 没有及时更新。用户通过编辑资料上传头像后，旧 `userInfo` 仍存 localStorage，新数据不完整。

**解决办法**：图片上传成功后调用 `refreshProfile()` 刷新 `userInfo`。

**预防**：涉及用户信息修改的操作后，都主动调用一次 `userStore.setUser()` 更新本地数据。

---

### #6 — 部署发现旧备份没有 `image_url` 等字段

**时间**：多次

**触发条件**：覆盖部署新代码时，复制了旧的 `db.sqlite3`（其中缺少 `services.image_url`、`users_user.nickname` 等字段）。

**错误信息**：`OperationalError: no such column: services.image_url`

**根因**：旧的数据库备份没有包含最新的字段列，而生产代码依赖这些字段。

**解决办法**：部署时用 `ALTER TABLE` 手动补字段：
```bash
sqlite3 db.sqlite3 "ALTER TABLE services ADD COLUMN image_url varchar(200);" 2>/dev/null
sqlite3 db.sqlite3 "ALTER TABLE users_user ADD COLUMN nickname varchar(50);" 2>/dev/null
```

**预防**：将这几条 `ALTER TABLE` 命令固定写进部署流程。

---

### #7 — 动态/帖子的后端 `PostListCreateView` 未传 `request` context

**时间**：2026-07-11

**触发条件**：在 `PostSerializer` 中新增了 `is_liked`、`is_favorited` 等字段，它们依赖 `self.context['request']` 来判断当前用户。但 `PostListCreateView.get()` 原来写的是 `PostSerializer(posts, many=True).data`，没有传 `context={'request': request}`。

**错误信息**：没有直接报错，但 `is_liked` 和 `is_favorited` 始终返回 `False`。

**根因**：`ModelSerializer` 的 `context` 默认不包含 `request`，需要显式传入。

**解决办法**：将所有 `PostSerializer(...).data` 改为 `PostSerializer(..., context={'request': request}).data`。

**预防**：凡是在 SerializerMethodField 中需要访问当前用户的，必须在序列化时主动传 `context`。

---

### #8 — `ConversationSerializer` 序列化时未传 `request` context

**时间**：2026-07-11

**触发条件**：在 `ConversationSerializer` 中新增了 `unread_count` 字段，依赖 `self.context['request'].user`。但在 `ConversationListCreateView` 和 `ConversationDetailView` 中，序列化时没有传 `context`。

**错误信息**：`conversations` API 返回 500 或 `unread_count` 为 0。

**根因**：同 #7，ModelSerializer 的 context 默认不含 request。

**解决办法**：将 `ConversationSerializer(convs, many=True).data` 改为 `ConversationSerializer(convs, many=True, context={'request': request}).data`。

**预防**：与 #7 相同，凡是在 SerializerMethodField 中需要访问当前用户的，必须传 `context`。

---

## 预防 checklist（修改前查阅）

- [ ] 新增模型后，所有引用它的文件都已加 import？
- [ ] `.vue` 文件的 CSS 修改优先用 Python 脚本而非 sed？
- [ ] Python 写入含换行符的 JS 代码时，转义处理正确？
- [ ] 新增/修改模型后，迁移文件已生成？
- [ ] 涉及当前用户的 Serializer，传了 `context={'request': request}`？
- [ ] 部署步骤中包含了所有需要跑的 migrate 命令？
- [ ] 旧数据库备份是否缺少新字段，需要 ALTER TABLE？

---

## 反思 (2026-07-11)

### Issue #13: Zip 结构错误导致部署失败

**现象**: 用户部署后 `manage.py` 找不到，`python manage.py` 报 `No such file or directory`。

**根因**: `zip -r ../booking-system-deploy.zip .` 从 `appointment_system/` 目录执行，zip里文件路径不带 `appointment_system/` 前缀。用户部署脚本期望文件在 `~/appointment_system/manage.py`，但实际解压到了 `~/manage.py`。

**经验教训**:
1. 给部署命令之前务必先验证产物：`unzip -l booking-system-deploy.zip | grep manage` — 一眼就能看出路径结构对不对
2. 排查"暂无服务"时应先确认部署是否成功（manage.py 是否存在），而不是直接看数据库和代码
3. PythonAnywhere 不托管 `/media/` 路径，头像直接存 base64 data URL 到数据库虽能工作但应提前说明利弊

---

## 反思 (2026-07-11) #2

### Issue #14: 漏引 AlipayConfirmView

**现象**: 部署后报 `NameError: name 'AlipayConfirmView' is not defined`

**根因**: 在 `views.py` 添加了 `AlipayConfirmView` 类，也在 `urls.py` 的 `urlpatterns` 里加了路由，但 `urls.py` 顶部的 `from .views import ...` 漏了导入。

**同样的问题在第 1 次部署时出现过**（`AdminCategoryCreateView` 漏引），说明我当时只改了路由列表，没检查导入语句。

**经验教训**:
1. 改 URL 路由时必须同步检查 import 行，这是重复踩坑
2. 应该在本地先 `python manage.py check` 验证再打包，能提前发现这类问题
3. notify_url 指向 Netlify（前端）而不是 PythonAnywhere（后端）是另一个低级错误 —— 异步通知必须发到后端域名
4. 支付回调的 return_url 和 notify_url 不应该从 HTTP_REFERER 动态派生，前端域名和后端域名不同，必须分开硬编码
