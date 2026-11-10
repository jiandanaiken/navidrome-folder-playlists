# Navidrome Discussions 帖子稿（发帖时直接粘贴）

> 发布位置：https://github.com/navidrome/navidrome/discussions
> 建议分类：Show and tell（如果没有就选 Q&A 或 Ideas）。发帖后把 `<仓库链接>` 替换成你的仓库地址。

---

**标题（英文）：**
Tip: Turn your physical folders into playlists with Smart Playlists (.nsp) — with a batch generator

**正文（英文）：**

Hi all! Smart Playlists (from #1417) can emulate "folders as playlists" — add/remove songs in a folder and the playlist updates itself. One non-obvious finding from testing on 0.64.2: **the artist/album tree shown in the UI/API is tag-based (virtual), but the `filepath` field in smart playlist rules matches the real path on disk.** They often disagree, which is why folder-based playlists built this way actually work.

Minimal example (`playlist_rules/MyFolder.nsp` anywhere in your library):

```json
{
  "name": "My Folder",
  "all": [
    { "startsWith": { "filepath": "My Folder/" } }
  ],
  "sort": "dateadded",
  "order": "desc"
}
```

Notes from practice:

- Use `startsWith` with a **trailing slash**, not `contains` — substring matching wrongly pulls in look-alike folders ("Foo" vs "Foo & Bar").
- `filepath` is relative to the MusicFolder (no `/music/` prefix since 0.56).
- Renaming an imported `.nsp` file re-imports it as a *new* playlist — rename via the `name` field instead.
- I wrote a small script that generates one `.nsp` per physical folder in one go (it also merges case-duplicate folder names): **<仓库链接>**

Feedback welcome!

---

**（可选）中文版标题：**
技巧：用智能播放列表（.nsp）把物理文件夹变成歌单，附批量生成脚本

**（可选）中文版正文要点：**
Navidrome 界面里的歌手/专辑树是按标签虚拟的，但智能歌单的 `filepath` 匹配的是磁盘真实路径——所以可以用它实现「文件夹=歌单」，文件夹加歌删歌歌单自动更新。注意用 `startsWith` 带尾斜杠而不是 `contains`（避免误伤同名前缀文件夹），路径写相对 MusicFolder 的相对路径。批量生成脚本见：<仓库链接>。思路来自 flemmingss.com 的博客（中文圈有 bilibili 转载），本仓库补充了批量脚本和实测细节。
