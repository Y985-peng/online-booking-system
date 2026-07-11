# 前端错误日志

---

## #1 — `CssSyntaxError: Unknown word |`

**时间**：2026-07-11

**原因**：用 `sed` 命令改 `.vue` 文件中的 CSS，sed 语法错误导致残留了 `*text-align: left;|` 等无效字符。

**修复**：搜索清理文件中残留的垃圾字符。

**预防**：改 `.vue` 文件的 CSS 优先用 Python 脚本（`content.replace()`）而不是 sed，因为 `.vue` 里 HTML/JS/CSS 混杂，sed 容易破坏结构。

---

## #2 — `Unterminated string constant`

**时间**：2026-07-11

**原因**：Python 脚本往 `.vue` 注入 JS 代码时，`\n` 被 Python 解释为真正的换行符，导致 JS 字符串跨行。

**修复**：改用 `'[转发] ' + ` 拼接或 JavaScript 模板字符串。

**预防**：Python 写 JS 字符串时，换行符用 `\\n` 或 raw string。更简单：不让 Python 处理含换行符的 JS。

---

## #3 — `Element is missing end tag`

**时间**：2026-07-11

**原因**：删除退出登录按钮时，Python 脚本把 `<div>` 和 `</div>` 一起删了，留下了一个空 `<div>` 没有闭合。

**修复**：找到并删除残留的空 `<div>`。

**预防**：删除 HTML 元素时，确保对应的开/闭标签都正确移除。

---

## #4 — 头像显示"我"而不是用户真实头像

**时间**：2026-07-11

**原因**：`userStore.userInfo?.avatar` 没有及时更新。用户上传头像后，localStorage 中的 `userInfo` 还是旧的。

**修复**：上传头像成功后调用 `userStore.setUser()` 刷新。

**预防**：修改用户信息后主动刷新 store。

---

## #5 — PC 端看不到右上角齿轮图标

**时间**：2026-07-11

**原因**：齿轮图标用了 `position:absolute` 相对于 header 定位。在 PC 端 DesktopLayout 的嵌套结构中，`position:relative` 的父容器宽度/高度计算异常导致图标溢出不可见。

**修复**：改用 flexbox 的 `margin-left:auto` 右对齐，移除 `position:relative` / `position:absolute`。

**预防**：跨平台的定位优先用 flexbox 布局而非 absolute。

---

## #6 — PC 端看不到导航栏中的图标/按钮

**时间**：2026-07-11

**原因**：在 `MyServices.vue` 中用了 `van-nav-bar` 并在 right slot 中放了一个 `+` 图标。但 DesktopLayout 的 CSS 有 `.main-content :deep(.van-nav-bar) { display: none; }`，导致 PC 端整个导航栏被隐藏，加号图标不可见。

**修复**：改用自定义 header div（不用 `van-nav-bar`），同时加上"发布服务"文字标签而不是只有图标。

**预防**：每次修改前端都要 PC 端和移动端双端适配。

---

## #7 — 前端 catch 块不显示具体错误信息，导致调试困难

**时间**：2026-07-11

**原因**：`Admin.vue` 中所有 API 调用的 catch 块都只显示固定文字（"添加失败"、"删除失败"等），没有显示服务端返回的具体错误信息，导致用户和开发者都不知道实际的问题是什么。

**修复**：将 catch 块改为：
```js
} catch (e) { alert(e?.response?.data?.message || '添加失败') }
```

**预防**：所有 API 调用的 catch 块都应该显示服务端的错误消息，而不是写死的文字。

---

## #8 — PC 端侧边栏缺少"分类"导航项

**时间**：2026-07-11

**原因**：`DesktopLayout.vue` 的 `navItems` 数组中只包含首页、搜索、动态、消息、订单、个人，没有添加"分类"项。移动端 tab 栏有分类图标，但 PC 端侧边栏没有对应的入口。

**修复**：在 `navItems` 中添加 `{ path: '/categories', icon: 'apps-o', label: '分类', isChat: false }`。

**预防**：在 PC 端或移动端新增页面后，检查两端的导航是否都添加了对应入口（App.vue 的 tabbar + DesktopLayout.vue 的 navItems）。

---

## #9 — `deleteFeedPost` 函数未定义导致删除按钮点不动

**时间**：2026-07-11

**原因**：在 `PostList.vue` 中给帖子卡片添加删除按钮（`@click.stop="deleteFeedPost(p)"`），但 `deleteFeedPost` 函数定义在之前多次修改中被误删了。模板引用了不存在的函数，点击无反应且控制台无报错。

**修复**：在 `PostList.vue` 脚本中补充 `deleteFeedPost` 函数定义。

**预防**：
- 修改 `.vue` 文件后，grep 确认所有模板中调用的函数都在脚本中有定义
- 涉及事件绑定的修改，手动点击测试验证
