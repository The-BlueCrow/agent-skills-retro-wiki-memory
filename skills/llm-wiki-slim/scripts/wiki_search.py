#!/usr/bin/env python3
"""wiki_search.py — wiki + raw 原始资料关键词检索（stdlib 零依赖）
用法:
  wiki_search.py <关键词...> [--raw] [--regex] [--context N] [--glob PATTERN]
  <关键词>    多词空格分隔 = AND（全部命中才算，带不带引号都行）
               同一词内 词1|词2 = OR（自动按 | 拆开、各自转义后合并；
               --regex 模式下整个查询交给正则，| 即正则的 OR）
  --raw       除 wiki 页外同时搜 raw/ 文本层（默认只搜 wiki 页）
  --regex     关键词按正则解释
  --context N 命中行前后各显示 N 行（默认 1）
  --glob      只搜匹配 glob 的文件（如 '*.md'）
"""
import re, sys, os, argparse, glob as globmod

def iter_files(roots, pattern):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ('.git', '__pycache__', '.venv', 'node_modules')]
            for fn in filenames:
                if pattern and not globmod.fnmatch.fnmatch(fn, pattern):
                    continue
                if fn.endswith(('.md', '.txt', '.py')):
                    yield os.path.join(dirpath, fn)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query', nargs='+', help='关键词；多词=AND，词1|词2=OR')
    ap.add_argument('--raw', action='store_true')
    ap.add_argument('--regex', action='store_true')
    ap.add_argument('--context', type=int, default=1)
    ap.add_argument('--glob', dest='glob', default=None)
    ap.add_argument('--limit', type=int, default=40, help='最多显示命中文件数')
    ap.add_argument('--wiki', default=None,
                    help='wiki 根目录（默认取环境变量 WIKI_PATH，再默认脚本所在目录——'
                         '原版设计为脚本置于 wiki 根内随库分发；本参数为通用化打包时新增，2026-10-26）')
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    base = a.wiki or os.environ.get('WIKI_PATH') or here
    roots = [base] if not a.raw else [base, os.path.join(base, 'raw')]
    # raw 已在 here 下，重复无害；显式分开是为了以后 raw 移出 wiki 目录也能搜到

    query = ' '.join(a.query)
    if a.regex:
        try:
            pat = re.compile(query)
        except re.error as e:
            sys.exit(f'正则错误: {e}')
        terms = [pat]
    else:
        # 词1|词2 = OR：同一词内按 | 拆成候选，各自转义后合并成一个候选式；
        # 不同词之间仍是 AND（外层 all() 判定）
        terms = []
        for w in query.split():
            alts = [x for x in w.split('|') if x]
            if not alts:
                continue
            terms.append(re.compile('|'.join(re.escape(x) for x in alts)))
        if not terms:
            sys.exit('空查询')

    hits = 0
    for path in iter_files(roots, a.glob):
        try:
            lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
        except OSError:
            continue
        matched = []
        for i, line in enumerate(lines):
            if all(t.search(line) for t in terms):
                matched.append(i)
        if not matched:
            continue
        hits += 1
        if hits > a.limit:
            print(f'... (超过 {a.limit} 个文件，截断)')
            break
        rel = os.path.relpath(path, here)
        print(f'== {rel} ({len(matched)} 处)')
        shown = set()
        for i in matched[:8]:
            for k in range(max(0, i - a.context), min(len(lines), i + a.context + 1)):
                if k not in shown:
                    shown.add(k)
                    mark = '>' if k == i else ' '
                    print(f'{mark}{k+1:5d}| {lines[k][:150]}')
            if matched.index(i) < min(7, len(matched) - 1):
                print('  ...')
    if not hits:
        print('（无命中）')
    else:
        print(f'\n命中 {hits} 个文件')

if __name__ == '__main__':
    main()
