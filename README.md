# Navidrome Folder Playlists / 按物理文件夹听歌

> **中文** | [English](#english)

用 Navidrome 的智能播放列表（Smart Playlists / `.nsp` 文件），把你的**物理文件夹**变成歌单：文件夹里加歌删歌，歌单自动跟着变，不需要手动维护。

**核心发现**：Navidrome 网页和 App 里看到的「歌手/专辑」目录树是**按音乐标签虚拟出来的**，不是磁盘上的真实目录；但智能播放列表的 `filepath` 规则匹配的**正是磁盘上的物理路径**。这两者经常对不上（比如一个平铺的合集文件夹，界面里会显示成按歌手嵌套的树）。本仓库的方法只依赖后者，所以能做到真正的「文件夹 = 歌单」。

> 已在 Navidrome **0.64.2** 实测验证（Docker）。`.nsp` 的 `filepath` 从 **0.56** 起写相对路径即可（不再需要 `/music/` 前缀）。

---

## 30 秒上手

在音乐库根目录（或其任意子文件夹，推荐建一个 `歌单规则/`）放一个 `.nsp` 文件，内容如下：

```json
{
  "name": "林栖",
  "comment": "物理文件夹歌单",
  "all": [
    { "startsWith": { "filepath": "林栖/" } }
  ],
  "sort": "dateadded",
  "order": "desc"
}
```

**只需要改两处：**

| 字段 | 改成什么 |
| --- | --- |
| `name` | 歌单显示名（建议与文件夹同名） |
| `filepath` | 音乐库根目录下的**相对**文件夹路径，**结尾的 `/` 必须保留** |

保存为 UTF-8 编码，等下一次曲库扫描导入即可（`AutoImportPlaylists` 默认开启）。歌单里加歌删歌自动同步；**新建文件夹**需要多写一个对应的 `.nsp`。

## 为什么用 `startsWith` 而不是 `contains`

`contains` 是子串匹配，会误伤：规则 `contains "伍佰"` 会把「伍佰 & China Blue」的歌也卷进来；`startsWith "伍佰/"` 带尾斜杠则是精确的物理路径前缀匹配。同理可以规避大小写重名文件夹互相污染的问题。

## 批量生成

一个文件夹一个 `.nsp` 手写太慢？用脚本一次生成全部：

```bash
python3 scripts/gen_folder_playlists.py /path/to/你的音乐库 -o nsp_output
```

- 为每个包含音频文件的子文件夹生成一个 `.nsp`（默认只扫第一层，`--depth` 可调）
- 自动跳过隐藏目录和 `@eaDir`、`#recycle` 等系统目录
- 大小写重名的文件夹会自动合并为一个歌单（多条 `startsWith` 用 `any` 组合）

## 已知坑（实测踩过）

1. **改名 = 新歌单**：`.nsp` 导入后再改文件名，会被当作新歌单导入，旧的不会消失。要改歌单名请改文件**内容里的 `name` 字段**。
2. **`name` 不能重复**：两个歌单同名会撞车。
3. **改规则要等扫描**：修改 `.nsp` 后不是即时生效，等曲库扫描重新导入（Auto-import 开启时）。
4. **`filepath` 是物理路径，且以 MusicFolder 为根**：不要带 `/music/` 这类挂载前缀（0.56+）。注意它和界面上显示的虚拟目录树不是一回事。
5. **没被 Navidrome 收录的文件不会出现在歌单里**：物理文件夹里的文件数可能多于歌单曲目数（未扫描、无标签、不支持的格式等），先触发一次扫描再对账。
6. 智能播放列表是官方 **Beta** 功能：歌单只读（不能手动调整曲目顺序）、`.nsp` 导入的歌单归属第一个 admin 账号。

## 字段与操作符速查

完整列表见[官方文档](https://www.navidrome.org/docs/usage/features/smart-playlists/)。常用的组合还有：

```json
{ "any": [ { "startsWith": { "filepath": "华语/" } }, { "startsWith": { "filepath": "粤语/" } } ] }
```

用 `any` 可以把多个文件夹并进一个歌单；`inPlaylist` 操作符还能引用其他歌单做嵌套。

## 出处与致谢

- 思路来源：[Use folders as playlists in Navidrome — flemmingss.com](https://flemmingss.com/use-folders-as-playlists-in-navidrome/)；中文圈传播：[bilibili 帖](https://www.bilibili.com/opus/892497365248770057)
- 功能出处：[navidrome/navidrome#1417 Smart Playlists](https://github.com/navidrome/navidrome/issues/1417)（现为官方 Beta 功能）
- 本仓库增量：中文教程、批量生成脚本、虚拟目录树 vs `filepath` 物理路径的实测结论

## License

MIT

---

<a name="english"></a>
## English

Turn your **physical folders** into Navidrome playlists using Smart Playlists (`.nsp` files). Add or remove songs in a folder and the playlist updates itself — no manual maintenance.

**Key finding**: the artist/album tree shown in Navidrome's UI and API is **built from tags (virtual)**, but the `filepath` field in smart playlist rules matches the **real path on disk**. They often disagree (a flat "various artists" folder shows up as a nested per-artist tree). This repo's approach relies only on the real path — that's what makes true "folder = playlist" possible.

Tested on Navidrome **0.64.2** (Docker). Since **0.56**, `filepath` takes a path relative to your music folder (no `/music/` prefix).

### Quick start

Drop a `.nsp` file into your music library root (or a `playlist_rules/` subfolder):

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

Only two things to change: `name` (playlist title) and `filepath` (folder path **relative** to the music root, **trailing slash required**). Save as UTF-8; the library scan imports it (`AutoImportPlaylists` is on by default).

Use `startsWith` with a trailing slash instead of `contains` — substring matching wrongly pulls in look-alike folders ("Foo" vs "Foo & Bar").

### Batch generation

```bash
python3 scripts/gen_folder_playlists.py /path/to/music -o nsp_output
```

Generates one `.nsp` per subfolder containing audio files, merging case-duplicate folder names into one playlist.

### Known pitfalls

- **Renaming an imported `.nsp` file creates a *new* playlist** (the old one stays). Rename via the `name` field instead.
- Duplicate `name` values collide.
- Rule edits take effect on the next library scan.
- Files not indexed by Navidrome (unsupported/untagged/not yet scanned) won't appear in the playlist.
- Smart Playlists are an official **Beta** feature: playlists are read-only; `.nsp`-imported playlists belong to the first admin user.

### Credits

- Idea: [flemmingss.com](https://flemmingss.com/use-folders-as-playlists-in-navidrome/) · [navidrome#1417](https://github.com/navidrome/navidrome/issues/1417)
- This repo adds: a batch generator script, and the verified finding that API paths are virtual while `filepath` rules match real disk paths.
