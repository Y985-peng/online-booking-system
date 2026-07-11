# 后端错误日志

---

## #1 — `NameError: name 'Notification' is not defined`

**时间**：2026-07-10

**原因**：`posts/serializers.py` 中新加的 `NotificationSerializer` 引用了 `Notification` 模型，但文件顶部 `from .models import ...` 漏写了 `Notification`。

**修复**：
```bash
sed -i 's/from .models import Post, PostLike, PostFavorite, PostComment, Follow/from .models import Post, PostLike, PostFavorite, PostComment, Follow, Notification/' posts/serializers.py
```

**预防**：新增模型后，检查所有引用该模型的文件是否都加了 import。

---

## #2 — `OperationalError: no such column: services.image_url`

**时间**：多次

**原因**：部署时复制的旧 `db.sqlite3` 没有 `image_url` 等字段。

**修复**：
```bash
sqlite3 db.sqlite3 "ALTER TABLE services ADD COLUMN image_url varchar(200);" 2>/dev/null
sqlite3 db.sqlite3 "ALTER TABLE users_user ADD COLUMN nickname varchar(50);" 2>/dev/null
```

**预防**：固定写进部署流程。

---

## #3 — `no such table` / 新增模型后部署没跑迁移

**原因**：新增 `PostLike`、`PostFavorite`、`PostComment`、`Notification` 等模型后，服务器没有执行 `migrate`。

**修复**：
```bash
python manage.py migrate posts
```

**预防**：部署步骤中必须包含所有新模型的迁移命令。

---

## #4 — Serializer 未传 `request` context

**原因**：`PostSerializer`、`ConversationSerializer` 的 `SerializerMethodField` 中需要 `self.context['request'].user`，但序列化时没传 `context={'request': request}`。

**修复**：将 `Serializer(...).data` 改为 `Serializer(..., context={'request': request}).data`。

**预防**：凡是在 SerializerMethodField 中需要访问当前用户的，必须传 context。

---

## #5 — 数据库字段缺失

**原因**：新代码依赖的字段在旧数据库备份中不存在。

**修复**：`ALTER TABLE` 手动补充。

**预防**：部署流程中包含了所有 ALTER TABLE 命令。

---

## #6 — 迁移文件没打包进 zip，部署后需要手动 makemigrations

**时间**：2026-07-11

**原因**：本地改了模型（给 Service 加了 `work_start`/`work_end` 字段），`makemigrations services` 生成了迁移文件。但在打包 zip 之前没有确认迁移文件存在，导致部署到服务器后迁移文件缺失。

**表现**：
```
Your models in app(s): 'services' have changes that are not yet reflected in a migration
```

**修复**：
```bash
python manage.py makemigrations services
python manage.py migrate services
```

**预防**：
- 模型改动后，先确认迁移文件已生成（`ls */migrations/0*.py`）
- 再打包 zip
- 部署步骤中必须包含所有 app 的 migrate 命令
- 每次打包前执行一次 `python manage.py makemigrations --check` 检查是否有未迁移的改动

---

## #7 — `services/urls.py` 语法错误：`from .views import ..., (`

**时间**：2026-07-11

**原因**：用 `sed` 往 `services/urls.py` 添加新 view 的 import 时，直接把字符串插在了 `from .views import (` 前面，导致变成 `from .views import AdminCategoryCreateView, AdminCategoryDeleteView, (` — 多余的 `(` 导致 SyntaxError。

**表现**：
```
from .views import AdminCategoryCreateView, AdminCategoryDeleteView, (
                                                                         ^
SyntaxError: invalid syntax
```

**修复**：重写 `services/urls.py`，把新 import 放进括号内正确的多行格式。

**预防**：
- 改 `urls.py` 的 import 时，确认现有格式是单行还是多行括号，用相应方式添加
- 不要用 `sed` 改 Python 的 import 语句，优先用 Python 脚本或手动重写

---

## #8 — `ImportError: cannot import name 'AdminCategoryCreateView'`

**时间**：2026-07-11

**原因**：`services/urls.py` 中 import 了 `AdminCategoryCreateView`，但这个类在 `services/views.py` 中并不存在。Python 脚本的 `content.replace()` 因原文模式不匹配而失败，新类没有被写入文件。

**表现**：
```
from .views import (
ImportError: cannot import name 'AdminCategoryCreateView' from 'services.views'
```

**修复**：在 `services/views.py` 中直接添加 `AdminCategoryCreateView` 和 `AdminCategoryDeleteView` 两个类定义。

**预防**：
- 用 `content.replace()` 替换代码块时，先确认原文模式精确匹配（`grep -A` 查看实际内容）
- 替换后 grep 确认新内容已写入
- 部署前本地跑一次 `python manage.py check` 检查 import 是否完整

---

## ⚠️ 高频重复错误：`sed` 改 `urls.py` 导致 `SyntaxError: invalid syntax`

**出现次数**：3 次（services/urls.py × 2, posts/urls.py × 1）

**错误模式**：
```
from .views import AdminCategoryCreateView, AdminCategoryDeleteView, (
                                                                         ^
SyntaxError: invalid syntax
```

**根因**：用 `sed` 往原有的多行括号 import（`from .views import (\n    ...`）前追加新类名，结果变成：
```python
from .views import NewView1, NewView2, (       ← , ( 导致语法错误
    OldView1, OldView2,
)
```

**反复发生的原因**：每次都没记住之前的教训，继续用 `sed` 改 Python 的 import 语句。

**正确做法**：
- 不要用 `sed` 改 Python 的 `import` 语句
- 直接重写整个 `urls.py` 文件（或者用 Python 脚本来修改）
- 添加新 view 后，部署前本地跑一次 `python manage.py check` 验证语法

**checklist**（每次加新 API 路由前查阅）：
- [ ] 确认 `urls.py` 的 import 格式：如果是多行括号形式，新类名放在括号内
- [ ] 确认 `views.py` 中存在对应的类定义
- [ ] 确认 `views.py` 中所有必要的 import 都已添加（`IsAuthenticated`、`get_object_or_404` 等）

---

## #9 — `OperationalError: duplicate column name: work_end`

**时间**：2026-07-11

**原因**：`services` 的迁移文件 `0002` 包含了 `work_start`、`work_end` 和 `ServiceCategory` 三个改动。但这个迁移文件之前已经部分应用过（`work_start` 和 `work_end` 字段已通过其他方式添加到数据库），再次 `migrate` 时尝试重复添加 `work_end` 列导致冲突。

**表现**：
```
django.db.utils.OperationalError: duplicate column name: work_end
```

**修复**：
```bash
python manage.py migrate services --fake
```

标记该迁移为已应用，跳过重复的列添加。

**预防**：
- 模型字段改动尽量分开放在独立的迁移文件中
- 部署前确认迁移文件和数据库状态一致
- 迁移冲突时用 `--fake` 跳过已执行部分

---

## #10 — `duplicate column name: nickname`（users 迁移冲突）

**时间**：2026-07-11

**原因**：与 #9 相同——`nickname` 列之前已通过 `ALTER TABLE` 手动添加，但迁移文件 `users.0002` 又尝试添加一次。

**修复**：
```bash
python manage.py migrate users --fake
```

**预防**：与 #9 相同，迁移冲突时 `--fake` 跳过多余列。

---

## #11 — `CategorySerializer` 未定义导致"分类添加失败"

**时间**：2026-07-11

**原因**：`services/serializers.py` 中用 `sed` 添加 `CategorySerializer` 类的命令没有成功执行，文件中只有 `ServiceCategory` 的 import 却没有对应的 Serializer 类。`AdminCategoryCreateView` 调用 `from .serializers import CategorySerializer` 时失败。

**表现**：前端点击"添加"后提示"添加失败"，后端无具体报错（被 catch 吞掉了）。

**修复**：在 `serializers.py` 末尾追加 `CategorySerializer` 类定义。

**预防**：
- 用 `sed` 加代码后必须 `grep` 确认内容已写入
- 涉及 API 调用的功能，前端 catch 块最好显示具体错误信息（`e?.response?.data?.message`）

---

## #12 — `CategoryListView` 返回格式从字符串改为对象，前端未同步更新

**时间**：2026-07-11

**原因**：`CategoryListView` 从返回 `['医疗','美容',...]`（字符串列表）改为返回 `[{'id':1,'name':'医疗'},...]`（对象列表），但前端 `CategoryList.vue` 仍按字符串格式处理，导致 `{{ cat }}` 渲染为 `[object Object]`。

**表现**：管理后台和分类页面都显示"暂无分类"。

**修复**：前端 `CategoryList.vue` 中所有 `cat` 改为 `cat.name`、`:key="cat"` 改为 `:key="cat.id"`。

**预防**：API 返回格式变动时，同步检查所有前端调用方的代码是否需要更新。

---

## #13 — URL 参数名与 view 的 `lookup_field` 不匹配导致 500

**时间**：2026-07-11

**错误信息**：
```
AssertionError: Expected view ServiceDetailView to be called with 
a URL keyword argument named "id". Fix your URL conf
```

**原因**：`ServiceDetailView` 设置了 `lookup_field = 'id'`，但 `services/urls.py` 中的路由写的是 `path('<int:pk>/', ...)`。URL 捕获的参数名是 `pk`，view 却按 `id` 去取，导致 `get_object()` 断言失败。

**修复**：
```bash
sed -i 's/<int:pk>/<int:id>/g' services/urls.py
```

**预防**：
- 修改 view 的 `lookup_field` 时，同步检查 URL 中对应的参数名是否一致
- 部署前本地跑一次 `python manage.py check` 可以提前发现这类问题
