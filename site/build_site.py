"""Gera site/index.html (arquivo único) a partir de site/app.html + notas do Avaliador independente.

Uso (na raiz do repo ou de qualquer lugar): python3 site/build_site.py
Fontes (e SÓ estas):
- resultados/_avaliador/notas_avaliador.csv  (nota nova, nota antiga, %testes, rubrica nova por execução)
- resultados/*/*/*/run-N/avaliacao_avaliador.json  (juízes, itens da rubrica, duração, regra do grok-4.7-high,
  reexecução dos testes, incoerências da auditoria)
Os avaliacao.json antigos NÃO são lidos. A nota antiga vem da coluna nota_antiga do CSV do Avaliador.
- Ranking com N=30 (só run-1; as runs 2–4 da tarefa de consistência ficam fora), como em RELATORIO_AVALIADOR.md.
- Confere ranking, médias por empresa e notas antigas (mesmas 30) contra RELATORIO_AVALIADOR.md.
"""
import csv, json, glob, os, re, base64, subprocess, tempfile, statistics as S, collections as C

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
os.chdir(RAIZ)

ITENS = ['legibilidade', 'erros_bordas', 'idiomatico', 'manutenibilidade', 'documentacao_instrucoes']


def ler(p):
    try:
        return open(p, errors='replace').read()
    except FileNotFoundError:
        return ''


def m2(xs):  # igual a m() de scripts/avaliador_relatorio.py
    xs = [x for x in xs if x is not None]
    return round(S.mean(xs), 2) if xs else None


# ---- CSV do Avaliador
csvr = {}
for l in csv.DictReader(open('resultados/_avaliador/notas_avaliador.csv', newline='')):
    csvr[(l['combo'], l['tarefa'], int(l['run']))] = l
assert len(csvr) == 528, len(csvr)

# incoerências da auditoria → categorias curtas (o texto completo fica no RELATORIO_AVALIADOR.md)
CAT = [('parcial', r'^timeout com entrega parcial'), ('piloto', r'sobrescreveu o do piloto'),
       ('refeita', r'^execução refeita'), ('commits', r'alterado em 2 commits'),
       ('naocommit', r'mudanças não commitadas'), ('semantiga', r'^sem avaliacao.json antiga'),
       ('reexec', r'^reexecução dos testes deu')]

X, juiz_modelo = [], {}
for f in sorted(glob.glob('resultados/[cg]*/*/*/run-*/avaliacao_avaliador.json')):
    a = json.load(open(f))
    me = f"{a['modelo']}-{a['esforco']}"
    c = csvr[(me, a['tarefa'], a['run'])]
    nota = a['nota_final_10'] if a['nota_final_10'] is not None else 0.0
    # CSV e JSON do Avaliador têm de dizer a mesma coisa
    assert abs(float(c['nota_nova']) - nota) < 1e-9, (f, c['nota_nova'], nota)
    assert c['status'] == a['status'] and abs(float(c['pct_testes']) - a['pct_testes']) < 1e-9, f
    assert (c['rubrica_nova'] == '') == (a['rubrica_media_10'] is None), f
    assert a['consistencia_extra'] == (a['run'] > 1), f
    jz = {k: v['rubrica_10'] for k, v in a['juizes'].items() if v.get('rubrica_10') is not None}
    ji = {k: [v['itens'].get(i, 0) for i in ITENS] for k, v in a['juizes'].items()
          if v.get('rubrica_10') is not None and v.get('itens')}
    fal = [[k, x] for k, v in a['juizes'].items() for x in v.get('falhas', [])]
    inc = []
    for txt in a.get('incoerencias', []):
        for k, rx in CAT:
            if re.search(rx, txt):
                inc.append(k); break
        else:
            inc.append('outra')
    for k, v in a['juizes'].items():
        juiz_modelo[k] = v.get('modelo') or juiz_modelo.get(k)
    rr = a.get('reexecucao_testes') or {}
    o = {'e': a['empresa'], 'm': a['modelo'], 'x': a['esforco'], 't': a['tarefa'], 'r': a['run'],
         's': a['status'], 'd': round(a['duracao_agente_s'], 1), 'p': a['pct_testes'],
         'tp': a['testes_passados'], 'tt': a['testes_total'], 'rb': a['rubrica_media_10'],
         'j': jz, 'ji': ji, 'f': fal,
         'n': nota, 'na': float(c['nota_antiga']), 'inc': inc,
         'rx': [rr.get('passados'), rr.get('total')] if rr else None}
    g = a.get('regra_excepcional_grok_4_7_high')
    if g:
        assert me == 'grok-4.7-high'
        o['g'] = [g['nota_base'], g['fator'], g['regra']]
    X.append(o)
assert len(X) == 528, len(X)
assert sum('g' in x for x in X) == 13

# ---- conferência com RELATORIO_AVALIADOR.md
rel = ler('resultados/RELATORIO_AVALIADOR.md')
ref = {}
for lin in rel.split('## Ranking novo', 1)[1].split('## Ranking por empresa')[0].splitlines():
    mm = re.match(r'\|(\d+)\|(\S+)\|(\w+)\|\*\*([\d.]+)\*\*\|([\d.]+)\|', lin)
    if mm:
        ref[mm.group(2)] = [float(mm.group(4)), float(mm.group(5)), int(mm.group(1))]
assert len(ref) == 16, ref
ref_emp = {}
for lin in rel.split('## Ranking por empresa', 1)[1].split('##')[0].splitlines():
    mm = re.match(r'\|(\w+)\|([\d.]+)\|([\d.]+)\|', lin)
    if mm:
        ref_emp[mm.group(1)] = [float(mm.group(2)), float(mm.group(3))]
assert len(ref_emp) == 4, ref_emp

princ = [x for x in X if x['r'] == 1]
g = C.defaultdict(list)
for x in princ:
    g[f"{x['m']}-{x['x']}"].append(x)
nova = {}
for me, rs in g.items():
    assert len(rs) == 30, (me, len(rs))
    nova[me] = m2([r['n'] for r in rs])
    got = [nova[me], m2([r['na'] for r in rs])]
    assert got == ref[me][:2], (me, got, ref[me])
ordem = sorted(nova, key=lambda k: -nova[k])
assert [ref[k][2] for k in ordem] == list(range(1, 17)), ordem
emp_de = {f"{x['m']}-{x['x']}": x['e'] for x in X}
for e, (n, o) in ref_emp.items():
    assert m2([nova[k] for k in nova if emp_de[k] == e]) == n, e

# ---- textos do relatório (copiados, não reescritos)
def md(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', s)


rodada = ler('resultados/RODADA.md')
regras = [md(l[2:].strip()) for l in rodada.split('## Regras específicas', 1)[1].split('##')[0].splitlines()
          if l.startswith('- ')]
metodo = [md(l[2:].strip()) for l in rel.split('## Metodologia', 1)[1].split('##')[0].splitlines()
          if l.startswith('- ')]

# ---- fontes: subset woff2 em base64 (cai para fontes do sistema se não houver)
UNI = 'U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201D,U+2022,U+2026,U+2190-2194,U+2212,U+2248,U+2264-2265,U+25B2,U+25BC,U+00D7,U+03C3'


def fonte(nome, arq):
    p = glob.glob(f'/usr/share/fonts/**/{arq}', recursive=True)
    if not p:
        return ''
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, 'f.woff2')
        subprocess.run(['pyftsubset', p[0], f'--unicodes={UNI}', '--flavor=woff2', f'--output-file={out}',
                        '--layout-features=kern,liga,tnum,lnum'], check=True)
        b = base64.b64encode(open(out, 'rb').read()).decode()
    return (f"@font-face{{font-family:{nome};src:url(data:font/woff2;base64,{b}) format('woff2');"
            "font-weight:300 900;font-display:swap}")


fontes = fonte('Fredoka', 'Fredoka-VariableFont_wdth,wght.ttf') + fonte('Nunito', 'Nunito-VariableFont_wght.ttf')

dados = {'runs': X, 'ref': ref, 'refEmp': ref_emp, 'regras': regras, 'metodo': metodo, 'itens': ITENS, 'juiz_modelo': juiz_modelo}
js = json.dumps(dados, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = open(os.path.join(AQUI, 'app.html')).read()
html = html.replace('/*__FONTES__*/', fontes).replace('__DADOS__', js)
open(os.path.join(AQUI, 'index.html'), 'w').write(html)
print(f'site/index.html: {len(html)/1024:.0f} KB (dados {len(js)/1024:.0f} KB, fontes {len(fontes)/1024:.0f} KB); '
      f'ranking (N=30) e empresas conferem com RELATORIO_AVALIADOR.md')
for i, me in enumerate(ordem, 1):
    print(f'{i:2d}. {me:28s} {nova[me]:.2f}')
for e in sorted(ref_emp, key=lambda e: -ref_emp[e][0]):
    print(f'    {e:8s} {m2([nova[k] for k in nova if emp_de[k] == e]):.2f}')
