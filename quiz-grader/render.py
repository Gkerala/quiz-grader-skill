"""채점 결과 JSON(표준입력)을 단일 HTML 파일로 만든다. 표준 라이브러리만 쓴다.

사용: python render.py [출력경로] < result.json
입력: {"title","subtitle","sections":[{"name","rows":[{"n","q","a","c","v","note"}]}],"review":["..."]}
  v는 ○ △ ✕ 중 하나. 글 안의 **굵게**는 <b>로 바뀐다. 점수는 v를 세어 계산한다.
"""
import html, json, re, sys
from datetime import date

CSS = """:root{--bg:#fafaf7;--fg:#1f2328;--muted:#656d76;--line:#d8dce0;--card:#fff;--ok:#1a7f37;--ok-bg:#dafbe1;--mid:#9a6700;--mid-bg:#fff8c5;--no:#cf222e;--no-bg:#ffebe9}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--fg:#e6e8eb;--muted:#9aa4af;--line:#2d333b;--card:#161a20;--ok:#56d364;--ok-bg:#12261a;--mid:#e3b341;--mid-bg:#2b2410;--no:#ff7b72;--no-bg:#2d1618}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,"Malgun Gothic",sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:32px 0 10px}
.sub{color:var(--muted);margin:0 0 16px}
.score{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 0}
.score span{padding:6px 14px;border-radius:999px;font-weight:600}
.s-ok{background:var(--ok-bg);color:var(--ok)}.s-mid{background:var(--mid-bg);color:var(--mid)}.s-no{background:var(--no-bg);color:var(--no)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);table-layout:fixed}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left;overflow-wrap:anywhere;word-break:keep-all}
th{background:var(--bg);font-size:13px;color:var(--muted)}
col.n{width:44px}col.q{width:22%}col.m{width:19%}col.a{width:38%}col.v{width:15%}
.v{font-weight:700}.v.ok{color:var(--ok)}.v.mid{color:var(--mid)}.v.no{color:var(--no)}
.v small{display:block;font-weight:400;color:var(--muted);margin-top:2px}
.review li{margin:0 0 10px}
@media (max-width:720px){
table,thead,tbody,tr,th,td{display:block;width:100%}thead{display:none}
tr{border:1px solid var(--line);border-radius:8px;margin:0 0 12px;padding:6px 0;background:var(--card)}
td{border:0;padding:4px 12px}td::before{content:attr(data-l);display:block;font-size:12px;color:var(--muted)}
table{border:0;background:none}}"""
CLS = {"○": "ok", "△": "mid", "✕": "no"}
HEAD = "<thead><tr><th>#</th><th>문제</th><th>내 답</th><th>정답</th><th>판정</th></tr></thead>"
COLS = '<colgroup><col class="n"><col class="q"><col class="m"><col class="a"><col class="v"></colgroup>'


def esc(s):  # 이스케이프 후 **굵게**만 허용
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(str(s)))


def row(r):
    v = r.get("v", "")
    note = f"<small>{esc(r['note'])}</small>" if r.get("note") else ""
    cells = [("번호", r.get("n", "")), ("문제", r.get("q", "")), ("내 답", r.get("a", "")), ("정답", r.get("c", ""))]
    tds = "".join(f'<td data-l="{l}">{esc(x)}</td>' for l, x in cells)
    return f'<tr>{tds}<td data-l="판정" class="v {CLS.get(v, "")}">{esc(v)}{note}</td></tr>'


def render(d):
    rows = [r for s in d["sections"] for r in s["rows"]]
    cnt = {k: sum(r.get("v") == k for r in rows) for k in CLS}
    pills = "".join(f'<span class="s-{c}">{k} {cnt[k]}</span>' for k, c in CLS.items())
    body = "".join(
        f"<h2>{esc(s['name'])}</h2><table>{COLS}{HEAD}<tbody>{''.join(row(r) for r in s['rows'])}</tbody></table>"
        for s in d["sections"]
    )
    rev = "".join(f"<li>{esc(x)}</li>" for x in d.get("review", []))
    rev = f'<h2>복습 우선순위</h2><ol class="review">{rev}</ol>' if rev else ""
    t = esc(d.get("title", "채점 결과"))
    return (
        f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{t}</title>'
        f"<style>{CSS}</style></head><body><main><h1>{t}</h1>"
        f'<p class="sub">{esc(d.get("subtitle", ""))}</p>'
        f'<div class="score">{pills}<span style="font-weight:400">총 {len(rows)}문제</span></div>'
        f"{body}{rev}</main></body></html>"
    )


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else f"quiz-result-{date.today():%Y%m%d}.html"
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(data))
    print(out)
