#!/usr/bin/env python3
"""index.html の CSP（<meta http-equiv="Content-Security-Policy">）にある
インラインスクリプトの SHA-256 を、今のスクリプトの中身に合わせて書き直す。

index.html の <script> を編集したら必ず実行する（しないとページのスクリプトが動かなくなる）:
    python3 tools/update-csp.py          # 書き直す
    python3 tools/update-csp.py --check  # 合っているか確かめるだけ（合っていなければ終了コード 1）
    python3 tools/update-csp.py 別の.html  # index.html 以外のファイルを書き直す
"""
import base64, hashlib, pathlib, re, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
path = pathlib.Path(args[0]) if args else pathlib.Path(__file__).resolve().parent.parent / "index.html"
html = path.read_text(encoding="utf-8")
scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", re.sub(r"<!--.*?-->", lambda c: " " * len(c.group(0)), html, flags=re.S), flags=re.S)
hashes = ["'sha256-%s'" % base64.b64encode(hashlib.sha256(s.encode("utf-8")).digest()).decode() for s in scripts]
m = re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)', html)
if not m:
    sys.exit("CSP の meta タグが見つかりません")
policy = m.group(2)
new_policy, n = re.subn(r"(script-src )((?:'sha256-[A-Za-z0-9+/=]+' ?)*)", lambda g: g.group(1) + " ".join(hashes) + " ", policy, count=1)
if n != 1:
    sys.exit("script-src が見つかりません")
new_policy = re.sub(r"  +", " ", new_policy)
if "--check" in sys.argv:
    ok = new_policy == policy
    print("CSP のハッシュは最新です" if ok else "CSP のハッシュが古くなっています。python3 tools/update-csp.py を実行してください")
    sys.exit(0 if ok else 1)
path.write_text(html[: m.start(2)] + new_policy + html[m.end(2):], encoding="utf-8")
print("インラインスクリプト %d 個のハッシュを書き込みました" % len(hashes))
