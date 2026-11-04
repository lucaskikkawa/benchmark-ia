"""Gera site/index.html (arquivo único) a partir de site/app.html + notas do Avaliador independente.

Uso (na raiz do repo ou de qualquer lugar): python3 site/build_site.py
Fontes (e SÓ estas):
- resultados/_avaliador/notas_avaliador.csv  (nota nova, nota antiga, %testes, rubrica nova por execução)
- resultados/*/*/*/run-N/avaliacao_avaliador.json  (juízes, itens da rubrica, duração, regra do grok-4.7-high,
  reexecução dos testes, incoerências da auditoria)
Os avaliacao.json antigos NÃO são lidos. A nota antiga vem da coluna nota_antiga do CSV do Avaliador.
- Ranking com N=30 (só run-1; as runs 2–4 da tarefa de consistência ficam fora), como em RELATORIO_AVALIADOR.md.
- Confere ranking, médias por empresa e notas antigas (mesmas 30) contra RELATORIO_AVALIADOR.md.
Ranking B (limite de 7 min / 420 s, 12 combinações sem Grok):
- resultados/_avaliador/cenario_7min/notas_7min.csv (360 execuções: status, %testes, rubrica, nota_i, nota_ii)
- resultados/*/*/*/run-1/avaliacao_avaliador_7min.json (juízes das 70 refeitas); as outras 290 são as do Ranking A
- confere notas e posições nota_i/nota_ii, médias por empresa e high − medium contra resumo_7min.json
  (tolerância 0.005) e RELATORIO_7MIN.md; sys.exit com erro se algo não bater.
"""
import sys, csv, json, glob, os, re, base64, subprocess, tempfile, statistics as S, collections as C

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



def juizes(a):
    jz = {k: v['rubrica_10'] for k, v in a['juizes'].items() if v.get('rubrica_10') is not None}
    ji = {k: [v['itens'].get(i, 0) for i in ITENS] for k, v in a['juizes'].items()
          if v.get('rubrica_10') is not None and v.get('itens')}
    fal = [[k, x] for k, v in a['juizes'].items() for x in v.get('falhas', [])]
    return jz, ji, fal


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
    jz, ji, fal = juizes(a)
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

# ---- Ranking B: cenário 7 min (420 s)
def confere(c, msg):
    if not c:
        sys.exit(f'ERRO (Ranking B): {msg}')


B7 = 'resultados/_avaliador/cenario_7min/'
resumo = json.load(open(B7 + 'resumo_7min.json'))
A1 = {(f"{x['m']}-{x['x']}", x['t']): x for x in X if x['r'] == 1}
XB = []
for l in csv.DictReader(open(B7 + 'notas_7min.csv', newline='')):
    me, t = l['combo'], l['tarefa']
    a = A1.get((me, t))
    confere(a is not None and a['e'] == l['empresa'] != 'grok', f'{me}/{t} sem par no Ranking A')
    confere(l['status_oficial'] == a['s'] and abs(float(l['nota_oficial']) - a['n']) < 1e-9, f'{me}/{t}: nota oficial ≠ Ranking A')
    o = {k: a[k] for k in ('e', 'm', 'x', 't', 'r', 's', 'd', 'p', 'tp', 'tt', 'rb', 'j', 'ji', 'f')}
    rf = l['refeita'] == 'True'
    if rf:
        f = f"resultados/{a['e']}/{me}/{t}/run-1/avaliacao_avaliador_7min.json"
        confere(os.path.exists(f), f'falta {f}')
        b = json.load(open(f))
        jz, ji, fal = juizes(b)
        o.update(s=b['status'], d=round(b['duracao_agente_s'], 1), p=b['pct_testes'], tp=b['testes_passados'],
                 tt=b['testes_total'], rb=b['rubrica_media_10'], j=jz, ji=ji, f=fal)
        confere(abs(b['nota_final_10'] - float(l['nota_ii'])) < 1e-9, f'{f}: nota ≠ nota_ii do CSV')
    else:
        confere(a['s'] == 'ok', f'{me}/{t}: timeout oficial não refeito')
    confere(o['s'] == l['status_7min'] and o['rb'] is not None and abs(o['p'] - float(l['pct_7min'])) < 1e-9
            and abs(o['rb'] - float(l['rubrica_7min'])) < 1e-9, f'{me}/{t}: status/%testes/rubrica ≠ CSV')
    ni, nii = float(l['nota_i']), float(l['nota_ii'])
    confere(ni == (0.0 if o['s'] == 'timeout' else nii), f'{me}/{t}: nota_i ≠ regra timeout = 0')
    confere(abs(round(0.7 * o['p'] / 10 + 0.3 * o['rb'], 2) - nii) < 1e-9, f'{me}/{t}: nota_ii ≠ fórmula')
    o.update(ni=ni, nii=nii, na=a['n'], rf=int(rf), inc=[])
    XB.append(o)
confere(len(XB) == 360 and sum(x['rf'] for x in XB) == 70, f'{len(XB)} execuções no Ranking B')
gB = C.defaultdict(list)
for x in XB:
    gB[f"{x['m']}-{x['x']}"].append(x)
confere(len(gB) == 12 and all(len(v) == 30 for v in gB.values()), 'Ranking B precisa de 12 combinações × 30')
rel7 = ler(B7 + 'RELATORIO_7MIN.md')
rel7emp = {}
for lin in rel7.split('## (b)', 1)[1].split('##')[0].splitlines():
    mm = re.match(r'\|(\w+)\|([\d,]+)\|([\d,]+)\|([\d,]+)\|', lin)
    if mm:
        rel7emp[mm.group(1)] = {'nota_i': float(mm.group(3).replace(',', '.')), 'nota_ii': float(mm.group(4).replace(',', '.'))}
confere(len(rel7emp) == 3, rel7emp)
base_de = lambda m: next(p for p in m.split('-') if p.isalpha() and p not in ('claude', 'gpt', 'gemini'))
TOL = 0.005 + 1e-9
refB, refBEmp, refBhm = {}, {}, {}
for v, fld in (('nota_i', 'ni'), ('nota_ii', 'nii')):
    med = {me: S.mean(r[fld] for r in rs) for me, rs in gB.items()}
    rres = resumo['res']
    confere(set(med) == set(rres), 'combinações ≠ resumo_7min.json')
    for me in med:
        confere(abs(med[me] - rres[me][v]) <= TOL, f'{v} {me}: {med[me]:.4f} × resumo {rres[me][v]:.4f}')
        confere(abs(rres[me]['nota_oficial'] - S.mean(r['n'] for r in g[me])) <= TOL, f'nota_oficial {me} ≠ Ranking A')
    ordB = sorted(med, key=lambda k: -med[k])
    confere({me: i for i, me in enumerate(ordB, 1)} == resumo['pos'][v], f'posições {v} ≠ resumo: {ordB}')
    for me, i in resumo['pos'][v].items():
        refB.setdefault(me, {})[v] = [med[me], i]
    for e in ('claude', 'codex', 'gemini'):
        me_e = [me for me in med if emp_de[me] == e]
        m_csv, m_res = S.mean(med[k] for k in me_e), S.mean(rres[k][v] for k in me_e)
        confere(abs(m_csv - m_res) <= TOL and abs(m_csv - rel7emp[e][v]) <= TOL,
                f'média {e} {v}: {m_csv:.4f} × resumo {m_res:.4f} × RELATORIO_7MIN {rel7emp[e][v]}')
        refBEmp.setdefault(e, {})[v] = m_csv
    bases = sorted({gB[me][0]['m'] for me in gB})
    confere(sorted(base_de(m) for m in bases) == sorted(resumo['hm']), 'pares high/medium ≠ resumo')
    for m in bases:
        d = med[m + '-high'] - med[m + '-medium']
        confere(abs(d - resumo['hm'][base_de(m)][v]) <= TOL, f'high−medium {m} {v}: {d:+.4f} × resumo {resumo["hm"][base_de(m)][v]:+.4f}')
        refBhm.setdefault(m, {})[v] = d
# a conclusão escrita no site (plano.md, V2.2) tem de valer nos números
hmi = {base_de(m): v for m, v in refBhm.items()}
confere(all(hmi[k]['nota_i'] > -0.05 for k in ('haiku', 'opus', 'luna', 'sol')), 'claude/codex: high não empata/ganha com 7 min')
confere(hmi['argon']['nota_i'] < 0 < hmi['argon']['nota_ii'], 'argon: high só ganha na nota_ii')
confere(hmi['flash']['nota_i'] < 0 and hmi['flash']['nota_ii'] < 0, 'flash: high deixou de ser pior')
# 10-ambigua-claude: 0% = timeout sem entrega (Gemini e Grok), Codex 40 a 42 de 42 (analise_10_ambigua_claude.md)
amb = [x for x in X + XB if x['t'] == '10-ambigua-claude' and x['r'] == 1]
confere(all(x['s'] == 'timeout' and x['p'] == 0 for x in amb if x['e'] in ('gemini', 'grok')), '10-ambigua: Gemini/Grok')
cx = [x for x in amb if x['e'] == 'codex']
confere(len(cx) == 8 and all(x['tt'] == 42 and 40 <= x['tp'] <= 42 for x in cx), '10-ambigua: Codex 40 a 42 de 42')
confere('SEM DEFEITO NA TAREFA' in ler('resultados/_avaliador/analise_10_ambigua_claude.md'), '10-ambigua: análise não valida a tarefa')

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

dados = {'runs': X, 'runsB': XB, 'refB': refB, 'refBEmp': refBEmp, 'refBhm': refBhm, 'ref': ref, 'refEmp': ref_emp, 'regras': regras, 'metodo': metodo, 'itens': ITENS, 'juiz_modelo': juiz_modelo}
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
print('Ranking B (7 min) confere com resumo_7min.json e RELATORIO_7MIN.md (notas, posições, empresas, high − medium)')
for v in ('nota_i', 'nota_ii'):
    print(f'  {v}:')
    for me in sorted(refB, key=lambda k: refB[k][v][1]):
        print(f'  {refB[me][v][1]:2d}. {me:28s} {refB[me][v][0]:.2f}')
    print('    ' + ' · '.join(f'{e} {refBEmp[e][v]:.2f}' for e in refBEmp))
    print('    high−medium: ' + ' · '.join(f'{m} {refBhm[m][v]:+.2f}' for m in refBhm))
