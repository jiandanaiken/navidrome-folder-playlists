#!/usr/bin/env python3
"""
gen_folder_playlists.py — 为 Navidrome 批量生成「物理文件夹歌单」(.nsp 智能播放列表)

为音乐库中每个包含音频文件的子文件夹生成一个 .nsp 文件：
    { "all": [ { "startsWith": { "filepath": "<相对路径>/" } } ], ... }

用法:
    python3 gen_folder_playlists.py /path/to/music -o nsp_output
    python3 gen_folder_playlists.py /path/to/music -o nsp_output --depth 2 --min-files 3

说明:
- 规则匹配的是磁盘物理路径（相对 MusicFolder，尾斜杠防止子串误伤）
- 大小写不同的重名文件夹（如 Beyond/beyond）自动合并为一个歌单（any 组合多条 startsWith）
- 生成后把整个输出目录复制/移动进音乐库（或 PlaylistsPath），等扫描导入即可
- 详见 https://github.com/<you>/navidrome-folder-playlists
"""
import argparse
import json
import os
import sys

AUDIO_EXT = {
    ".mp3", ".wav", ".flac", ".ape", ".dsf", ".dff", ".ogg", ".oga",
    ".m4a", ".wma", ".opus", ".aiff", ".aif",
}
SKIP_DIRS = {"@eaDir", "#recycle", "$RECYCLE.BIN", "System Volume Information", "lost+found"}


def count_audio_deep(path):
    """目录下音频文件数（递归子目录），用于判定该文件夹是否值得生成歌单"""
    n = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in AUDIO_EXT:
                n += 1
    return n


def scan_folders(root, depth, min_files, excludes):
    """返回 [(相对路径, 文件夹名)]，按路径排序；depth=1 只看第一层。
    含歌判定按整棵子树递归统计（否则「歌全在子文件夹里的合集」会被漏掉），
    但规则仍按该文件夹自身的物理前缀匹配（天然覆盖其下所有层）。"""
    results = []
    root = os.path.abspath(root)

    def walk(current, level):
        try:
            entries = sorted(os.scandir(current), key=lambda e: e.name)
        except OSError as e:
            print(f"  跳过（无法读取）: {current} ({e})", file=sys.stderr)
            return
        for entry in entries:
            if not entry.is_dir(follow_symlinks=False):
                continue
            if entry.name.startswith(".") or entry.name in SKIP_DIRS:
                continue
            if any(pat.lower() in entry.name.lower() for pat in excludes):
                continue
            rel = os.path.relpath(entry.path, root).replace(os.sep, "/")
            if count_audio_deep(entry.path) >= min_files:
                results.append((rel, entry.name))
            if level < depth:
                walk(entry.path, level + 1)

    walk(root, 1)
    return results


def merge_case_duplicates(folders):
    """大小写不敏感归并：[(rel, name)...] -> {key: [(rel, name)...]}"""
    groups = {}
    for rel, name in folders:
        groups.setdefault(name.lower(), []).append((rel, name))
    return groups


def build_nsp(name, rels):
    """rels: 该歌单覆盖的物理相对路径列表（1 条或多条 any 组合）"""
    conds = [{"startsWith": {"filepath": rel + "/"}} for rel in rels]
    rule = {"any": conds} if len(conds) > 1 else conds[0]
    return {
        "name": name,
        "comment": "物理文件夹歌单: " + ", ".join(rels),
        "all": [rule],
        "sort": "dateadded",
        "order": "desc",
    }


def main():
    ap = argparse.ArgumentParser(description="为 Navidrome 批量生成物理文件夹歌单 (.nsp)")
    ap.add_argument("music_root", help="音乐库根目录（即 Navidrome MusicFolder 指向的目录）")
    ap.add_argument("-o", "--output", default="nsp_output", help="输出目录（默认 ./nsp_output）")
    ap.add_argument("--depth", type=int, default=1, help="扫描深度：1=只看第一层子目录（默认），2=含第二层")
    ap.add_argument("--min-files", type=int, default=1, help="文件夹至少含几个音频文件才生成歌单（默认 1）")
    ap.add_argument("--exclude", action="append", default=[], help="排除文件夹名包含该关键词（可多次）")
    args = ap.parse_args()

    root = os.path.abspath(args.music_root)
    if not os.path.isdir(root):
        sys.exit(f"错误: 音乐库根目录不存在: {root}")

    folders = scan_folders(root, args.depth, args.min_files, args.exclude)
    if not folders:
        sys.exit("没有找到包含音频文件的文件夹，检查路径与 --min-files。")

    groups = merge_case_duplicates(folders)
    os.makedirs(args.output, exist_ok=True)

    used_names = set()
    written = 0
    for key in sorted(groups):
        rels = [rel for rel, _ in groups[key]]
        name = groups[key][0][1]
        while name in used_names:
            name += "_"
        used_names.add(name)
        out = os.path.join(args.output, name + ".nsp")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(build_nsp(name, rels), f, ensure_ascii=False, indent=2)
            f.write("\n")
        written += 1

    print(f"完成: 生成 {written} 个 .nsp -> {args.output}/")
    print("下一步: 把输出目录整个复制进音乐库（如 音乐/歌单规则/），触发一次曲库扫描即可。")


if __name__ == "__main__":
    main()
