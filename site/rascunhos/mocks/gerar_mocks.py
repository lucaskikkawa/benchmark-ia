"""Gera os mocks estáticos (390x844) de cada aba a partir de resultados/ (mesma fórmula de rodada_relatorio.py).

Uso (na raiz do repo): python3 site/rascunhos/mocks/gerar_mocks.py  → site/rascunhos/mocks/mock-<aba>.html
Render: google-chrome --headless --window-size=390,844 --screenshot=site/rascunhos/mocks/mock-<aba>.png site/rascunhos/mocks/mock-<aba>.html
"""
import json, glob, os, math, statistics as S, collections as C

R = []
for f in glob.glob('resultados/[cg]*/*/*/run-*/resultado.json'):
    r = json.load(open(f)); a = json.load(open(f.replace('resultado.json', 'avaliacao.json')))
    r['rub'] = a['rubrica_10'] or 0
    r['jz'] = {k: v['rubrica_10'] for k, v in a['juizes'].items() if v.get('rubrica_10') is not None}
    r['ji'] = {k: v['itens'] for k, v in a['juizes'].items() if v.get('rubrica_10') is not None and v.get('itens')}
    r['obs'] = a.get('obs', []); r['me'] = f"{r['modelo']}-{r['esforco']}"; r['tipo'] = r['tarefa'][:2]
    r['autora'] = r['tarefa'].split('-')[-1]
    r['sem'] = 0.7 * r['pct_passados'] / 10 + 0.3 * r['rub']
    r['nota'] = 0 if r['status'] == 'timeout' else r['sem']
    R.append(r)
assert len(R) == 528
m = lambda x: S.mean(x) if x else 0
EMP = ['claude', 'codex', 'gemini', 'grok']
TIPOS = ['01 função', '02 bug', '03 refatoração', '04 dados', '05 cli', '06 multiarquivo', '07 performance',
         '08 testes', '09 api', '10 ambígua']
TIPOS_C = ['01 função', '02 bug', '03 refator.', '04 dados', '05 cli', '06 multiarq.', '07 perf.', '08 testes',
           '09 api', '10 ambígua']
COR = {'claude': '#E06A1E', 'codex': '#C3C8D0', 'gemini': '#3B6FE0', 'grok': '#1C1B22'}
g = C.defaultdict(list)
for r in R: g[r['me']].append(r)
emp_de = {me: rs[0]['empresa'] for me, rs in g.items()}
nota = {me: m([r['nota'] for r in rs]) for me, rs in g.items()}
rank = sorted(g, key=lambda me: -nota[me])
fmt = lambda x: f"{x:.2f}"


def split(me):
    return me.rsplit('-', 1)

# ---------------------------------------------------------------- peças comuns
CSS = """
:root{--bg:#FFF8EC;--card:#fff;--ink:#2B2340;--ink2:#6B6280;--sun:#FFD23F;--orange:#FF9F1C;--up:#2FB86B;--down:#E5484D;
  --claude:#E06A1E;--codex:#C3C8D0;--gemini:#3B6FE0;--grok:#1C1B22;--line:#E7E0F0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:390px;height:844px;overflow:hidden}
body{background:var(--bg);background-image:radial-gradient(rgba(43,35,64,.07) 1.5px,transparent 1.6px);background-size:18px 18px;
  color:var(--ink);font-family:Nunito,ui-rounded,system-ui,sans-serif;font-variant-numeric:tabular-nums;position:relative}
.f{font-family:Fredoka,Nunito,sans-serif}
.box{background:var(--card);border:3px solid var(--ink);border-radius:20px;box-shadow:4px 4px 0 var(--ink)}
header{padding:14px 16px 0;display:flex;align-items:center;gap:10px}
.bubble{position:relative;background:var(--sun);border:3px solid var(--ink);border-radius:18px;padding:6px 14px 4px;transform:rotate(-2deg);box-shadow:3px 3px 0 var(--ink)}
.bubble h1{font-family:Fredoka,sans-serif;font-weight:700;font-size:30px;line-height:1}
.bubble:after{content:"";position:absolute;right:-12px;bottom:6px;width:16px;height:16px;background:var(--sun);border-right:3px solid var(--ink);border-bottom:3px solid var(--ink);transform:rotate(-45deg)}
.bubble.sm{padding:3px 10px 2px;border-radius:14px}.bubble.sm h1{font-size:20px}.bubble.sm:after{width:12px;height:12px;right:-9px;bottom:4px}
.sub{font-size:12px;color:var(--ink2);font-weight:700;line-height:1.25}
.crew{display:flex;gap:2px;margin-left:auto}.crew svg{width:34px;height:34px}
.pill{margin-left:auto;font-size:11px;font-weight:800;border:2px solid var(--ink);border-radius:12px;background:#fff;padding:2px 8px;box-shadow:2px 2px 0 var(--ink);white-space:nowrap}
h2{font-family:Fredoka,sans-serif;font-size:20px;margin:12px 16px 6px;display:flex;align-items:center;gap:8px;line-height:1.1}
h2 .tag{font-family:Nunito;font-size:11px;font-weight:800;background:var(--sun);border:2px solid var(--ink);border-radius:10px;padding:1px 7px;transform:rotate(2deg)}
h3{font-family:Fredoka,sans-serif;font-size:14px;font-weight:600;display:flex;justify-content:space-between;align-items:baseline}
h3 small{font-family:Nunito;font-size:11px;font-weight:800;color:var(--ink2)}
.card{margin:8px 20px 0 16px;padding:8px 12px}
.chip{display:inline-block;font-size:10px;font-weight:800;border:2px solid var(--ink);border-radius:8px;padding:0 5px;margin-left:3px;vertical-align:1px;background:#fff;line-height:1.35}
.chip.high{background:repeating-linear-gradient(45deg,#fff 0 3px,#E7E0F0 3px 6px)}
.leg{display:flex;gap:12px;font-size:11px;font-weight:800;color:var(--ink2);align-items:center;flex-wrap:wrap}
.leg i{display:inline-block;width:12px;height:12px;border:2px solid var(--ink);border-radius:50%;vertical-align:-2px;margin-right:3px}
.tip{margin:8px 20px 0 16px;padding:5px 10px;line-height:1.2;display:flex;gap:8px;align-items:center;font-size:12px;font-weight:700;background:#FFF3C4;border-radius:16px}
.tip svg{flex:none}
.seg{display:flex;margin:0 20px 0 16px;border:3px solid var(--ink);border-radius:14px;overflow:hidden;background:#fff;box-shadow:2px 2px 0 var(--ink)}
.seg span{flex:1;text-align:center;font-size:11px;font-weight:800;padding:4px 2px;line-height:1.15}
.seg span+span{border-left:2px solid var(--ink)}.seg .on{background:var(--sun)}
.sw{flex:none;display:inline-block;width:38px;height:22px;border-radius:12px;border:3px solid var(--ink);background:#EDE6F5;position:relative}
.sw:after{content:"";position:absolute;top:1px;left:1px;width:14px;height:14px;border-radius:50%;background:#fff;border:2px solid var(--ink)}
.sw.on{background:var(--up)}.sw.on:after{left:17px}
nav{position:absolute;left:10px;right:10px;bottom:8px;height:56px;display:flex;justify-content:space-around;align-items:center;border-radius:22px;background:var(--ink);box-shadow:0 4px 0 #0E0B18}
nav a{color:#fff;text-decoration:none;font-size:10px;font-weight:800;text-align:center;line-height:1.2;width:62px;border:2px solid transparent;padding:3px 0;border-radius:14px}
nav a span{display:block;font-size:20px}
nav a.on{background:var(--sun);color:var(--ink);border-color:#fff}
svg text{font-family:Nunito,sans-serif;font-weight:800;fill:var(--ink)}
"""


def robo(id_, cor, rosto, extra):
    """Robô-terminal: cabeça arredondada na cor da empresa, rosto '>' + '_'."""
    return f'''<symbol id="{id_}" viewBox="0 0 40 40">{extra}
  <rect x="5" y="10" width="30" height="25" rx="7" fill="{cor}" stroke="#2B2340" stroke-width="2.5"/>
  <path d="M8 14 q0-2 2-2 h4" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-linecap="round"/>
  <path d="M12 18 l5.5 4 -5.5 4" fill="none" stroke="{rosto}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="20.5" y1="28" x2="28" y2="28" stroke="{rosto}" stroke-width="2.8" stroke-linecap="round"/>
</symbol>'''


ANT = '<line x1="{x}" y1="{y}" x2="{x}" y2="10" stroke="#2B2340" stroke-width="2.5"/>'
SYMBOLS = '<svg width="0" height="0" style="position:absolute"><defs>' + \
    robo('m-claude', COR['claude'], '#2B2340',  # Clô: antena com faísca de 4 pontas
         ANT.format(x=20, y=5) + '<path d="M20 0.5 l1.3 2.9 2.9 1.3 -2.9 1.3 -1.3 2.9 -1.3 -2.9 -2.9 -1.3 2.9 -1.3z" fill="#FFD23F" stroke="#2B2340" stroke-width="1.1" stroke-linejoin="round"/>') + \
    robo('m-codex', COR['codex'], '#2B2340',  # Códi: antena de bolinha + orelhas
         ANT.format(x=20, y=5) + '<circle cx="20" cy="4.5" r="2.8" fill="#FFD23F" stroke="#2B2340" stroke-width="1.5"/>'
         '<rect x="1.5" y="18" width="4" height="9" rx="2" fill="#2B2340"/><rect x="34.5" y="18" width="4" height="9" rx="2" fill="#2B2340"/>') + \
    robo('m-gemini', COR['gemini'], '#fff',  # Gêmi: duas antenas (as "gêmeas")
         ANT.format(x=13, y=4) + ANT.format(x=27, y=4) +
         '<circle cx="13" cy="4" r="2.4" fill="#8FB0FF" stroke="#2B2340" stroke-width="1.4"/><circle cx="27" cy="4" r="2.4" fill="#8FB0FF" stroke="#2B2340" stroke-width="1.4"/>') + \
    robo('m-grok', COR['grok'], '#fff',  # Gróqui: sem antena, parafusos laterais e viseira
         '<rect x="10" y="5.5" width="20" height="5" rx="2.5" fill="#6B6280" stroke="#2B2340" stroke-width="1.8"/>'
         '<circle cx="3.5" cy="22.5" r="3" fill="#FFD23F" stroke="#2B2340" stroke-width="1.6"/><circle cx="36.5" cy="22.5" r="3" fill="#FFD23F" stroke="#2B2340" stroke-width="1.6"/>') + \
    '''<symbol id="toga" viewBox="0 0 40 30"><path d="M7 2 h26 l5 27 h-36z" fill="#2B2340"/><path d="M14 2 l6 9 6-9" fill="#fff" stroke="#2B2340" stroke-width="1.5" stroke-linejoin="round"/></symbol>
<pattern id="hach" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff"/><rect width="2.2" height="5" fill="#2B2340" fill-opacity=".55"/></pattern>
</defs></svg>'''

ABAS = [('ranking', '🏆', 'Ranking'), ('comparar', '⚖️', 'Comparar'), ('esforco', '🔥', 'Esforço'),
        ('tarefas', '🧩', 'Tarefas'), ('juizes', '🧑‍⚖️', 'Juízes')]


def nav(ativa):
    return '<nav aria-label="abas">' + ''.join(
        f'<a{" class=on aria-current=page" if k == ativa else ""} href="#{k}"><span>{ic}</span>{t}</a>' for k, ic, t in ABAS) + '</nav>'


# Checagem embutida: marca no <title> o que vaza da tela, encosta na barra de abas ou corta texto.
CHECK = """<script>addEventListener('load',()=>{const nb=document.querySelector('nav').getBoundingClientRect().top,p=[];
for(const e of document.querySelectorAll('body *')){if(e.closest('nav')||e.closest('defs')||e.tagName==='symbol')continue;const r=e.getBoundingClientRect();if(!r.width&&!r.height)continue;
if(r.right>390.5||r.left<-0.5)p.push('x:'+(e.className.baseVal??e.className)+':'+e.tagName);
if(r.bottom>nb-2)p.push('y:'+e.tagName+'.'+(e.className.baseVal??e.className)+':'+Math.round(r.bottom));
if(e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflow!=='visible')p.push('corte:'+e.tagName+'.'+e.className)}
document.title='CHECK '+(p.length?[...new Set(p)].slice(0,8).join(' | '):'ok')+' nav='+Math.round(nb)})</script>"""


def pagina(aba, corpo, titulo):
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rodada 1 — mock {titulo}</title><style>{CSS}</style></head>
<body>{SYMBOLS}
{corpo}
{nav(aba)}
{CHECK}
</body></html>
'''


def mini_header(titulo, emoji, tag=None):
    t = f' <span class="tag">{tag}</span>' if tag else ''
    return f'''<header><div class="bubble sm"><h1>Rodada 1</h1></div>
<span class="pill">⚖️ 70% testes · ⏱ timeout = 0</span></header>
<h2>{emoji} {titulo}{t}</h2>'''


def ico(e, s=32):
    return f'<svg width="{s}" height="{s}" aria-hidden="true"><use href="#m-{e}"/></svg>'


def nome_chip(me):
    mo, x = split(me)
    return f'{mo}<span class="chip{" high" if x == "high" else ""}">{x}</span>'


# ---------------------------------------------------------------- 1. ranking
def aba_ranking():
    st = C.Counter(r['status'] for r in R)
    linhas = []
    for i, me in enumerate(rank, 1):
        if i in (6, 7, 8): continue
        e = emp_de[me]; mo, x = split(me); rs = g[me]
        to = sum(r['status'] == 'timeout' for r in rs)
        mv = f'<span class="mv dn">⏱ {to}</span>' if to > 1 else '<span class="mv">—</span>'
        bar_bg = f'background-color:var(--{e})'
        linhas.append(f'''<div class="li"><span class="pos">{i}</span>{ico(e)}
  <div><div class="nm">{nome_chip(me)}</div><div class="bar{" high" if x == "high" else ""}"><i style="width:{nota[me]*10:.1f}%;{bar_bg}"></i></div></div>
  <div class="sc">{fmt(nota[me])}{mv}</div>{'<span class="crown">👑</span>' if i == 1 else ''}</div>''')
        if i == 5: linhas.append('<div class="gap">· · · 6º a 8º · · ·</div>')
        if i == 10: break
    bf = 'grok-4.7-build-fast-medium'; sem = m([r['sem'] for r in g[bf]])
    corpo = f'''<style>
.stats{{display:flex;gap:8px;padding:12px 20px 0 16px}}.stat{{flex:1;padding:6px 8px 5px;text-align:center;border-radius:16px}}
.stat b{{display:block;font-family:Fredoka,sans-serif;font-size:22px;line-height:1.05}}.stat span{{font-size:11px;font-weight:800;color:var(--ink2)}}.stat.t b{{color:var(--down)}}
.ctrl{{margin:10px 20px 0 16px;padding:8px 14px 10px}}.ctrl .row{{display:flex;justify-content:space-between;align-items:baseline}}
.lbl{{font-weight:800;font-size:13px}}.val{{font-family:Fredoka,sans-serif;font-size:14px;font-weight:600}}
.slider{{position:relative;height:26px;margin:6px 0 4px}}.track{{position:absolute;top:8px;left:0;right:0;height:12px;border:3px solid var(--ink);border-radius:10px;background:linear-gradient(90deg,var(--sun) 0 70%,#EDE6F5 70% 100%)}}
.thumb{{position:absolute;left:calc(70% - 15px);top:-2px;width:30px;height:30px;border-radius:50%;background:var(--orange);border:3px solid var(--ink);box-shadow:2px 2px 0 var(--ink);display:grid;place-items:center;font-size:14px}}
.ends{{display:flex;justify-content:space-between;font-size:11px;font-weight:800;color:var(--ink2)}}
.toggles{{display:flex;gap:8px;margin-top:10px}}.tg{{flex:1;display:flex;align-items:center;gap:7px;border:3px solid var(--ink);border-radius:14px;padding:6px 8px;font-size:12px;font-weight:800;line-height:1.1;background:#fff;box-shadow:2px 2px 0 var(--ink)}}
.rank{{margin:0 20px 0 16px;padding:2px 10px}}
.li{{position:relative;display:grid;grid-template-columns:22px 32px 1fr 44px;align-items:center;gap:6px;padding:3px 0;border-bottom:2px dashed var(--line)}}.li:last-child{{border-bottom:0}}
.pos{{font-family:Fredoka,sans-serif;font-weight:700;font-size:17px;text-align:center}}
.nm{{font-weight:800;font-size:13px;line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.bar{{height:10px;border:2px solid var(--ink);border-radius:6px;margin-top:4px;background:#F4F0F8;overflow:hidden}}.bar i{{display:block;height:100%;border-right:2px solid var(--ink)}}
.bar.high i{{background-image:repeating-linear-gradient(45deg,rgba(255,255,255,.5) 0 3px,transparent 3px 7px)}}
.sc{{font-family:Fredoka,sans-serif;font-weight:700;font-size:17px;text-align:right}}.mv{{font-size:10px;font-weight:800;display:block;text-align:right;line-height:1}}.mv.dn{{color:var(--down)}}
.crown{{position:absolute;left:30px;top:-7px;font-size:14px;transform:rotate(-15deg)}}
.more{{text-align:center;font-size:12px;font-weight:800;color:var(--ink2);padding:2px 0}}.gap{{text-align:center;font-size:11px;font-weight:800;color:var(--ink2);padding:1px 0;border-bottom:2px dashed var(--line)}}
</style>
<header><div><div class="bubble"><h1>Rodada 1</h1></div>
<p class="sub" style="margin-top:8px">16 modelos × esforço · 40 tarefas<br>29/10 19:07 → 30/10 01:27</p></div>
<div class="crew" aria-label="mascotes">{''.join(ico(e, 34) for e in EMP)}</div></header>
<section class="stats"><div class="stat box"><b>{len(R)}</b><span>execuções</span></div>
<div class="stat box t"><b>{st['timeout']}</b><span>⏱ timeouts</span></div><div class="stat box"><b>{st['erro']}</b><span>⚠ erros de cota</span></div></section>
<section class="ctrl box"><div class="row"><span class="lbl">⚖️ Peso da nota</span><span class="val">70% testes · 30% rubrica</span></div>
<div class="slider"><div class="track"></div><div class="thumb">💡</div></div><div class="ends"><span>🧑‍⚖️ só rubrica</span><span>só testes 🧪</span></div>
<div class="toggles"><div class="tg"><span class="sw on"></span>Timeout<br>vale zero</div><div class="tg"><span class="sw"></span>Ignorar erros<br>de cota</div></div></section>
<h2>🏆 Ranking ao vivo <span class="tag">padrão do relatório</span></h2>
<section class="rank box">{''.join(linhas)}<div class="more">▾ ver os 16 · toque num modelo para a ficha</div></section>
<div class="tip box">{ico('grok', 30)}<span>Desligue <b>“Timeout vale zero”</b>: grok-4.7-build-fast-medium pula de {fmt(nota[bf])} para <b>{fmt(sem)}</b>!</span></div>'''
    return pagina('ranking', corpo, 'ranking')


# ---------------------------------------------------------------- 2. comparar
def stats_me(me):
    rs = g[me]; it = C.defaultdict(list)
    for r in rs:
        if r['ji']:
            for k in next(iter(r['ji'].values())): it[k].append(m([v[k] for v in r['ji'].values()]))
    eixos = [m(it['legibilidade']) / 2, m(it['erros_bordas']) / 2, m(it['idiomatico']) / 2, m(it['manutenibilidade']) / 2,
             m(it['documentacao_instrucoes']) / 2, m([r['pct_passados'] for r in rs]) / 100,
             1 - sum(r['status'] == 'timeout' for r in rs) / len(rs)]
    tipos = [m([r['nota'] for r in rs if r['tipo'] == f'{i:02d}']) for i in range(1, 11)]
    return eixos, tipos, m([r['duracao_agente_s'] for r in rs])


def aba_comparar():
    A, B = 'claude-haiku-5-5-high', 'gpt-6-luna-medium'
    ea, ta, tma = stats_me(A); eb, tb, tmb = stats_me(B)
    rot = ['Legível', 'Bordas', 'Idiomático', 'Manutenção', 'Docs', 'Testes', 'Pontual']
    cx, cy, rr, n = 180, 96, 66, 7
    ang = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]
    pt = lambda i, v: (cx + rr * v * math.cos(ang[i]), cy + rr * v * math.sin(ang[i]))
    poly = lambda vs: ' '.join(f'{x:.1f},{y:.1f}' for x, y in (pt(i, v) for i, v in enumerate(vs)))
    grade = ''.join(f'<polygon points="{poly([k] * n)}" fill="none" stroke="#E7E0F0" stroke-width="1.5"/>' for k in (.25, .5, .75, 1))
    raios = ''.join(f'<line x1="{cx}" y1="{cy}" x2="{pt(i,1)[0]:.1f}" y2="{pt(i,1)[1]:.1f}" stroke="#E7E0F0" stroke-width="1.5"/>' for i in range(n))
    rots = ''
    for i, t in enumerate(rot):
        x, y = pt(i, 1.2); anc = 'middle' if abs(x - cx) < 8 else ('start' if x > cx else 'end')
        rots += f'<text x="{x:.1f}" y="{y+4:.1f}" font-size="10.5" text-anchor="{anc}" fill="#6B6280">{t}</text>'
    pontos = ''.join(f'<circle cx="{pt(i,v)[0]:.1f}" cy="{pt(i,v)[1]:.1f}" r="3.5" fill="{COR["claude"]}" stroke="#fff" stroke-width="1.5"/>' for i, v in enumerate(ea))
    radar = f'''<svg width="332" height="190" viewBox="0 0 332 190" role="img" aria-label="radar da rubrica">{grade}{raios}
<polygon points="{poly(eb)}" fill="{COR['codex']}" fill-opacity=".55" stroke="#2B2340" stroke-width="2" stroke-dasharray="5 3" stroke-linejoin="round"/>
<polygon points="{poly(ea)}" fill="{COR['claude']}" fill-opacity=".22" stroke="{COR['claude']}" stroke-width="2.5" stroke-linejoin="round"/>{pontos}{rots}
<text x="{cx+4}" y="{cy-rr*.5+3:.1f}" font-size="8.5" fill="#A79FB6">50%</text></svg>'''
    linhas = ''; va = 0
    for i in range(10):
        a, b = ta[i], tb[i]; va += a > b
        sa, sb = ('★ ', '') if a > b else (('', ' ★') if b > a else ('', ''))
        linhas += f'''<div class="mr"><span class="va">{sa}{a:.2f}</span><div class="l"><i style="width:{a*10:.0f}%"></i></div>
<span class="tp">{TIPOS_C[i]}</span><div class="r"><i style="width:{b*10:.0f}%"></i></div><span class="vb">{b:.2f}{sb}</span></div>'''
    corpo = f'''<style>
.duelo{{display:flex;align-items:center;gap:8px;margin:2px 20px 0 16px}}
.carta{{flex:1;display:flex;align-items:center;gap:6px;padding:5px 8px;border-radius:16px;font-size:12px;font-weight:800;line-height:1.15}}
.carta small{{display:block;font-size:10px;color:var(--ink2)}}.vs{{font-family:Fredoka;font-weight:700;font-size:18px}}
.mr{{display:grid;grid-template-columns:46px 1fr 76px 1fr 46px;align-items:center;gap:4px;height:19px}}
.mr .l,.mr .r{{height:11px;display:flex}}.mr .l{{justify-content:flex-end}}
.mr i{{display:block;height:100%;border:2px solid var(--ink)}}.mr .l i{{background:var(--claude);border-radius:5px 0 0 5px;background-image:repeating-linear-gradient(45deg,rgba(255,255,255,.5) 0 3px,transparent 3px 7px)}}
.mr .r i{{background:var(--codex);border-radius:0 5px 5px 0}}
.tp{{font-size:10.5px;font-weight:800;text-align:center;color:var(--ink2);white-space:nowrap}}
.va,.vb{{font-family:Fredoka;font-weight:600;font-size:12px}}.va{{text-align:right}}
.placar{{display:flex;gap:8px;margin:8px 20px 0 16px}}.placar>div{{flex:1;padding:5px 10px;border-radius:16px;font-size:11.5px;font-weight:800;line-height:1.2}}
.placar b{{font-family:Fredoka;font-size:18px;display:block}}
</style>
{mini_header('Duelo de modelos', '⚖️')}
<div class="duelo"><div class="carta box">{ico('claude', 30)}<span>{nome_chip(A)}<small>A · {fmt(nota[A])}</small></span></div><span class="vs">×</span>
<div class="carta box">{ico('codex', 30)}<span>{nome_chip(B)}<small>B · {fmt(nota[B])}</small></span></div></div>
<section class="card box"><h3>Rubrica, testes e pontualidade <small>0–100%</small></h3>{radar}
<div class="leg"><span><i style="background:var(--claude)"></i>A — linha cheia</span><span><i style="background:var(--codex);border-style:dashed"></i>B — tracejada</span></div></section>
<section class="card box"><h3>Nota por tipo de tarefa <small>◀ A · B ▶</small></h3>{linhas}</section>
<div class="placar"><div class="box">🏅 A vence em<b>{va} de 10 tipos</b></div><div class="box">⏱ tempo médio<b>{tma:.0f} s × {tmb:.0f} s</b></div></div>'''
    return pagina('comparar', corpo, 'comparar')


# ---------------------------------------------------------------- 3. esforço
def aba_esforco():
    mods = sorted({split(me)[0] for me in g})
    linhas = []
    for mo in mods:
        a, b = mo + '-medium', mo + '-high'
        ta = m([r['duracao_agente_s'] for r in g[a]]); tb = m([r['duracao_agente_s'] for r in g[b]])
        linhas.append((mo, emp_de[a], nota[a], nota[b], ta, tb))
    linhas.sort(key=lambda t: -(t[3] - t[2]))
    W, x0, x1 = 334, 128, 280
    X = lambda v: x0 + (x1 - x0) * v / 10
    h = 26; y0 = 18
    svg = ''.join(f'<line x1="{X(v):.1f}" y1="10" x2="{X(v):.1f}" y2="{y0+h*8-6}" stroke="#EFE9F5" stroke-width="1.5"/><text x="{X(v):.1f}" y="8" font-size="9" text-anchor="middle" fill="#6B6280">{v}</text>' for v in (0, 2.5, 5, 7.5, 10))
    piorou = 0
    for i, (mo, e, a, b, ta, tb) in enumerate(linhas):
        y = y0 + i * h + 8; d = b - a; up = d > 0; piorou += d < 0
        cor = '#2FB86B' if up else '#E5484D'
        nm = mo.replace('grok-4.7-build-fast', 'grok-4.7-b-fast')
        svg += f'''<use href="#m-{e}" x="0" y="{y-10}" width="20" height="20"/><text x="23" y="{y+4}" font-size="11">{nm}</text>
<line x1="{X(a):.1f}" y1="{y}" x2="{X(b):.1f}" y2="{y}" stroke="{cor}" stroke-width="4" stroke-linecap="round"/>
<circle cx="{X(a):.1f}" cy="{y}" r="6" fill="{COR[e]}" stroke="#2B2340" stroke-width="2"/>
<circle cx="{X(b):.1f}" cy="{y}" r="6" fill="url(#hach)" stroke="#2B2340" stroke-width="2"/>
<text x="{W}" y="{y+4}" font-size="11.5" text-anchor="end"><tspan fill="{cor}">{"▲" if up else "▼"}</tspan> {f'{d:+.2f}'.replace('-','−')}</text>'''
    hd = y0 + h * 8
    T0, T1, tmax = 118, 262, 210
    TX = lambda s: T0 + (T1 - T0) * s / tmax
    th = 17
    ts = ''.join(f'<line x1="{TX(s):.1f}" y1="10" x2="{TX(s):.1f}" y2="{12+th*8}" stroke="#EFE9F5" stroke-width="1.5"/><text x="{TX(s):.1f}" y="8" font-size="9" text-anchor="middle" fill="#6B6280">{s}s</text>' for s in (0, 60, 120, 180))
    for i, (mo, e, a, b, ta, tb) in enumerate(sorted(linhas, key=lambda t: t[4])):
        y = 20 + i * th
        nm = mo.replace('grok-4.7-build-fast', 'grok-4.7-b-fast')
        dx = -4 if tb > ta else 4
        ts += f'''<text x="0" y="{y+4}" font-size="10.5" fill="#6B6280">{nm}</text>
<line x1="{TX(ta):.1f}" y1="{y}" x2="{TX(tb)+dx:.1f}" y2="{y}" stroke="#2B2340" stroke-width="2"/>
<path d="M{TX(tb):.1f} {y} l{dx*1.5:.1f} -4 v8z" fill="#2B2340"/><circle cx="{TX(ta):.1f}" cy="{y}" r="3.5" fill="{COR[e]}" stroke="#2B2340" stroke-width="1.5"/>
<text x="{W}" y="{y+4}" font-size="10" text-anchor="end">{ta:.0f}→{tb:.0f}</text>'''
    # toggle "ignorar erros de cota" para o opus-high
    oh = [r for r in g['claude-opus-5-5-high'] if r['status'] != 'erro']; ohn = m([r['nota'] for r in oh])
    corpo = f'''<style>.verd{{display:flex;gap:10px;align-items:center;margin:8px 20px 0 16px;padding:6px 12px;background:var(--sun);transform:rotate(-1deg);border-radius:18px}}
.verd b{{font-family:Fredoka;font-size:17px;line-height:1.1;display:block}}.verd span{{font-size:11.5px;font-weight:800}}</style>
{mini_header('Mais esforço ajuda?', '🔥', 'medium → high')}
<section class="card box"><h3>Nota medium × high <small>0–10</small></h3>
<svg width="334" height="{hd}" viewBox="0 0 334 {hd}" role="img" aria-label="halteres medium x high">{svg}</svg>
<div class="leg"><span><i style="background:#6B6280"></i>medium (cor cheia)</span><span><i style="background:repeating-linear-gradient(45deg,#fff 0 2px,#8A8296 2px 4px)"></i>high (hachurada)</span><span>▲ melhorou ▼ piorou</span></div></section>
<section class="card box"><h3>Tempo médio medium → high <small>segundos</small></h3>
<svg width="334" height="{20+th*8}" viewBox="0 0 334 {20+th*8}" role="img" aria-label="tempo medio">{ts}</svg></section>
<div class="verd box">{ico('claude', 38)}<div><b>High piorou em {piorou} de 8 modelos 😬</b>
<span>Ligue “Ignorar erros de cota”: opus-high vai de {fmt(nota['claude-opus-5-5-high'])} para {fmt(ohn)}.</span></div></div>'''
    return pagina('esforco', corpo, 'esforço')


# ---------------------------------------------------------------- 4. tarefas
RAMPA = ['#FFF3C4', '#FFD23F', '#3B9C9C', '#2B2340']


def rampa(v):  # v 0..10, claro = pior
    t = max(0, min(1, v / 10)) * 3; i = min(2, int(t)); f = t - i
    a, b = RAMPA[i], RAMPA[i + 1]
    c = [round(int(a[k:k+2], 16) * (1 - f) + int(b[k:k+2], 16) * f) for k in (1, 3, 5)]
    return '#%02X%02X%02X' % tuple(c), (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) < 140


def aba_tarefas():
    cel = ''
    for i in range(10):
        t = f'{i+1:02d}'
        vs = [m([r['nota'] for r in R if r['empresa'] == e and r['tipo'] == t]) for e in EMP]
        dest = t in ('08', '10')
        cel += f'<span class="rl{" d" if dest else ""}">{TIPOS[i]}</span>'
        for e, v in zip(EMP, vs):
            bg, esc = rampa(v)
            mx = v == max(vs)
            cel += f'<span class="c{" esc" if esc else ""}" style="background:{bg}">{v:.1f}{"<em>★</em>" if mx else ""}</span>'
    bt = C.defaultdict(list)
    for r in R: bt[r['tarefa']].append(r['pct_passados'])
    tod = [t for t, v in sorted(bt.items()) if all(p == 100 for p in v)]
    quase = [t for t, v in sorted(bt.items()) if t not in tod and sum(p == 100 for p in v) / len(v) >= .9]
    grad = ', '.join(rampa(v)[0] for v in (0, 2.5, 5, 7.5, 10))
    corpo = f'''<style>
.hm{{display:grid;grid-template-columns:98px repeat(4,1fr);gap:3px;margin-top:4px}}
.hm .ch{{display:flex;flex-direction:column;align-items:center;font-size:10px;font-weight:800;line-height:1}}
.rl{{font-size:11.5px;font-weight:800;display:flex;align-items:center;white-space:nowrap}}.rl.d{{background:#FFF3C4;border-radius:6px;padding-left:3px;margin-left:-3px}}
.c{{height:26px;border:2px solid var(--ink);border-radius:7px;display:flex;align-items:center;justify-content:center;font-family:Fredoka;font-weight:600;font-size:13px;position:relative}}
.c.esc{{color:#fff}}.c em{{font-style:normal;font-size:9px;position:absolute;top:-1px;right:3px}}
.esc2{{display:flex;align-items:center;gap:6px;font-size:10.5px;font-weight:800;color:var(--ink2);margin-top:6px}}
.esc2 i{{flex:1;height:10px;border:2px solid var(--ink);border-radius:6px;background:linear-gradient(90deg,{grad})}}
.gab{{margin:8px 20px 0 16px;padding:6px 12px;font-size:11.5px;font-weight:700;line-height:1.3}}.gab b{{font-family:Fredoka;font-size:14px}}
.tg2{{display:inline-block;border:2px solid var(--ink);border-radius:8px;padding:0 5px;margin:1px 2px 0 0;font-weight:800;background:#E3F6EA}}
</style>
{mini_header('Mapa de tarefas', '🧩', 'tipo × empresa')}
<div class="seg"><span class="on">empresa<br>resolvedora</span><span>modelo ×<br>esforço</span><span>empresa<br>autora</span></div>
<section class="card box"><h3>Nota média (com penalidade) <small>★ = melhor da linha</small></h3>
<div class="hm"><span></span>{''.join(f'<span class="ch">{ico(e, 24)}{e}</span>' for e in EMP)}{cel}</div>
<div class="esc2">0 <i></i> 10 · claro = pior</div></section>
<div class="tip box">{ico('codex', 30)}<span><b>10 ambígua</b> é o único tipo em que o codex passa o claude. Em <b>08 testes</b>, gemini e grok mal pontuam.</span></div>
<div class="gab box"><b>✅ Todo mundo gabaritou</b><br>{''.join(f'<span class="tg2">{t}</span>' for t in tod)}
<span style="color:var(--ink2)"> e mais {len(quase)} quase (11 de 12 com 100%)</span></div>'''
    return pagina('tarefas', corpo, 'tarefas')


# ---------------------------------------------------------------- 5. juízes
def aba_juizes():
    ju = C.defaultdict(list)
    for r in R:
        for k, v in r['jz'].items(): ju[k].append(v)
    med = {k: m(v) for k, v in ju.items()}
    sev, boa = min(med, key=med.get), max(med, key=med.get)
    juizes = ''
    for e in EMP:
        sel = '<span class="sl">mais severo</span>' if e == sev else ('<span class="sl">mais bonzinho</span>' if e == boa else '')
        juizes += f'''<div class="jz"><svg width="54" height="62" viewBox="0 0 40 46" aria-hidden="true"><use href="#toga" x="0" y="16" width="40" height="30"/><use href="#m-{e}" x="0" y="0" width="40" height="40"/></svg>
<b>{med[e]:.2f}</b><span>{e} · n={len(ju[e])}</span>{sel}</div>'''
    fal = C.Counter()
    for r in R:
        for x in r['obs']:
            if 'falhou' in x: fal[(x.split()[0], x.split(':')[-1].strip())] += 1
    mx = max(fal[(e, 'JSON inválido')] + fal[(e, 'timeout')] for e in EMP)
    barras = ''
    for e in EMP:
        js, to = fal[(e, 'JSON inválido')], fal[(e, 'timeout')]
        seg = (f'<i class="js" style="width:{js/mx*100:.1f}%"></i>' if js else '') + (f'<i class="to" style="width:{to/mx*100:.1f}%"></i>' if to else '')
        barras += f'<div class="fb">{ico(e, 20)}<div class="tr">{seg or "<em>nenhuma falha</em>"}</div><span>{js + to}</span></div>'
    # dispersão: um ponto por execução com 2 juízes válidos, agrupado em grade inteira
    pares = []
    for r in R:
        if len(r['jz']) == 2:
            (ka, a), (kb, b) = sorted(r['jz'].items()); pares.append((a, b, r))
    cont = C.Counter((math.floor(a + .5), math.floor(b + .5)) for a, b, _ in pares if abs(a - b) <= 3)
    P0, PS = 30, 16  # origem e passo da grade
    PX = lambda v: P0 + v * PS; PY = lambda v: 8 + (10 - v) * PS
    sc = f'<rect x="{PX(0)}" y="{PY(10)}" width="{10*PS}" height="{10*PS}" fill="#FBF8FE" stroke="#E7E0F0"/>'
    sc += f'<line x1="{PX(0)}" y1="{PY(0)}" x2="{PX(10)}" y2="{PY(10)}" stroke="#2FB86B" stroke-width="2" stroke-dasharray="4 3"/>'
    for v in (0, 5, 10):
        sc += f'<text x="{PX(v)}" y="{PY(0)+14}" font-size="9" text-anchor="middle" fill="#6B6280">{v}</text><text x="{PX(0)-8}" y="{PY(v)+3}" font-size="9" text-anchor="end" fill="#6B6280">{v}</text>'
    for (a, b), n in sorted(cont.items(), key=lambda kv: -kv[1]):
        sc += f'<circle cx="{PX(a):.1f}" cy="{PY(b):.1f}" r="{1.8+math.sqrt(n)*0.95:.1f}" fill="#3B9C9C" fill-opacity=".55" stroke="#2B2340" stroke-width="1.2"/>'
    fora = [(a, b) for a, b, _ in pares if abs(a - b) > 3]
    for a, b in fora:
        sc += f'<circle cx="{PX(a):.1f}" cy="{PY(b):.1f}" r="5" fill="#fff" stroke="#E5484D" stroke-width="2.5"/><text x="{PX(a):.1f}" y="{PY(b)+3:.1f}" font-size="7" text-anchor="middle" fill="#E5484D">!</text>'
    dv = [abs(a - b) for a, b, _ in pares]
    sc_h = PY(0) + 26
    sc += f'<text x="{PX(5)}" y="{PY(0)+24}" font-size="9.5" text-anchor="middle" fill="#6B6280">juiz 1 (ordem alfabética)</text><text transform="translate(8 {PY(5)}) rotate(-90)" font-size="9.5" text-anchor="middle" fill="#6B6280">juiz 2</text>'
    corpo = f'''<style>
.trib{{display:flex;justify-content:space-between;margin:0 20px 0 16px;padding:6px 6px 6px}}
.jz{{width:25%;display:flex;flex-direction:column;align-items:center;line-height:1.1;position:relative}}
.jz b{{font-family:Fredoka;font-size:19px}}.jz>span{{font-size:10px;font-weight:800;color:var(--ink2)}}
.jz .sl{{position:absolute;top:-6px;background:var(--sun);border:2px solid var(--ink);border-radius:8px;font-size:9px;font-weight:800;color:var(--ink);padding:0 4px;white-space:nowrap;transform:rotate(-4deg)}}
.fb{{display:grid;grid-template-columns:22px 1fr 30px;align-items:center;gap:6px;height:22px}}
.fb .tr{{display:flex;gap:2px;height:13px}}.fb i{{display:block;height:100%;border:2px solid var(--ink);border-radius:4px}}
.fb .js{{background:#6B6280}}.fb .to{{background:repeating-linear-gradient(45deg,#fff 0 3px,#6B6280 3px 6px)}}
.fb em{{font-size:10.5px;font-weight:800;color:var(--ink2);font-style:normal}}.fb>span{{font-family:Fredoka;font-weight:600;font-size:13px;text-align:right}}
.dsp{{display:flex;gap:8px;align-items:flex-start}}.dsp svg{{flex:none}}.dsp p{{font-size:11px;font-weight:700;line-height:1.3;color:var(--ink2)}}.dsp p b{{color:var(--ink)}}
.vies{{display:flex;align-items:center;gap:6px;margin-top:6px;font-size:11px;font-weight:800;line-height:1.1}}
</style>
{mini_header('O tribunal', '🧑‍⚖️', 'nota média dada')}
<section class="trib box">{juizes}</section>
<section class="card box"><h3>Falhas dos juízes <small>tentativas</small></h3>{barras}
<div class="leg" style="margin-top:3px"><span><i style="background:#6B6280;border-radius:3px"></i>JSON inválido</span><span><i style="background:repeating-linear-gradient(45deg,#fff 0 2px,#6B6280 2px 4px);border-radius:3px"></i>timeout</span></div></section>
<section class="card box"><h3>Juiz 1 × juiz 2 <small>{len(pares)} execuções</small></h3>
<div class="dsp"><svg width="200" height="{sc_h:.0f}" viewBox="0 0 200 {sc_h:.0f}" role="img" aria-label="dispersao juiz 1 x juiz 2">{sc}</svg>
<p>Bolha = nº de execuções com o mesmo par de notas.<br>Na <b>linha verde</b> os juízes concordam.<br>|diferença| média <b>{m(dv):.2f}</b> pt · mediana <b>{S.median(dv):.2f}</b>.<br><b style="color:#E5484D">○ !</b> {len(fora)} casos com mais de 3 pts de briga.
<span class="vies"><span class="sw"></span>Corrigir viés dos juízes (experimento)</span></p></div></section>'''
    return pagina('juizes', corpo, 'juízes')


if __name__ == '__main__':
    for nome, fn in [('ranking', aba_ranking), ('comparar', aba_comparar), ('esforco', aba_esforco),
                     ('tarefas', aba_tarefas), ('juizes', aba_juizes)]:
        open(f'site/rascunhos/mocks/mock-{nome}.html', 'w').write(fn())
        print('site/rascunhos/mocks/mock-%s.html' % nome)
