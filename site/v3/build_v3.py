"""Gera site/v3/index.html (arquivo único, site 1.0) a partir de site/v3/app.html.

Uso (de qualquer lugar):
    python3 site/v3/build_v3.py                      # Rodada 1 + bloco v3 (auto: procura a rodada v3 em resultados/)
    python3 site/v3/build_v3.py --v3-json ARQ.json   # Rodada 1 + bloco v3 lido de um JSON pronto (formato no LEIA-ME)
    python3 site/v3/build_v3.py --v3-dir DIR         # procura a rodada v3 em DIR/gemini/gemini-4-{hydrogen,neon}-*/
    python3 site/v3/build_v3.py --mock               # QA: bloco v3 FALSO (cópia renomeada do Argon/Flash) em
                                                     #     site/v3/qa/mock/index-mock.html; NUNCA vai para o index.html

NÃO toca em site/index.html, site/app.html nem site/build_site.py (v2). A leitura e as conferências da Rodada 1
são as mesmas do build_site.py da v2 (copiadas aqui para não importar aquele script, que grava o index da v2):
- resultados/_avaliador/notas_avaliador.csv + resultados/*/*/*/run-N/avaliacao_avaliador.json (Ranking A)
- resultados/_avaliador/cenario_7min/ (Ranking B, 7 min) conferido contra resumo_7min.json e RELATORIO_7MIN.md
- RELATORIO_AVALIADOR.md (ranking com Grok, como no relatório; o site filtra o Grok só na interface)
"""
import sys, csv, json, glob, os, re, base64, subprocess, tempfile, argparse, statistics as S, collections as C

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(AQUI)
RAIZ = os.path.dirname(SITE)
os.chdir(RAIZ)

ap = argparse.ArgumentParser()
ap.add_argument('--v3-json')
ap.add_argument('--v3-dir', default='resultados')
ap.add_argument('--mock', action='store_true')
ARGS = ap.parse_args()

ITENS = ['legibilidade', 'erros_bordas', 'idiomatico', 'manutenibilidade', 'documentacao_instrucoes']
MODELOS_V3 = ['gemini-4-hydrogen-medium', 'gemini-4-hydrogen-high', 'gemini-4-neon-medium', 'gemini-4-neon-high']
PLACEHOLDER = 'aguardando rodada v3'


def ler(p):
    try:
        return open(p, errors='replace').read()
    except FileNotFoundError:
        return ''


def m2(xs):
    xs = [x for x in xs if x is not None]
    return round(S.mean(xs), 2) if xs else None


def falha(msg):
    sys.exit('ERRO: ' + msg)


# ======================================================================== Rodada 1 (igual à v2)
csvr = {}
for l in csv.DictReader(open('resultados/_avaliador/notas_avaliador.csv', newline='')):
    csvr[(l['combo'], l['tarefa'], int(l['run']))] = l
assert len(csvr) == 528, len(csvr)

CAT = [('parcial', r'^timeout com entrega parcial'), ('piloto', r'sobrescreveu o do piloto'),
       ('refeita', r'^execução refeita'), ('commits', r'alterado em 2 commits'),
       ('naocommit', r'mudanças não commitadas'), ('semantiga', r'^sem avaliacao.json antiga'),
       ('reexec', r'^reexecução dos testes deu')]


def juizes(a):
    jz = {k: v['rubrica_10'] for k, v in a['juizes'].items() if v.get('rubrica_10') is not None}
    ji = {k: [v['itens'].get(i, 0) for i in ITENS] for k, v in a['juizes'].items()
          if v.get('rubrica_10') is not None and v.get('itens')}
    return jz, ji


X, juiz_modelo = [], {}
for f in sorted(glob.glob('resultados/[cg]*/*/*/run-*/avaliacao_avaliador.json')):
    a = json.load(open(f))
    if a['modelo'] in ('gemini-4-hydrogen', 'gemini-4-neon'):
        continue  # rodada v3: vai para o bloco v3, não para a Rodada 1
    me = f"{a['modelo']}-{a['esforco']}"
    c = csvr[(me, a['tarefa'], a['run'])]
    nota = a['nota_final_10'] if a['nota_final_10'] is not None else 0.0
    assert abs(float(c['nota_nova']) - nota) < 1e-9, (f, c['nota_nova'], nota)
    assert c['status'] == a['status'] and abs(float(c['pct_testes']) - a['pct_testes']) < 1e-9, f
    jz, ji = juizes(a)
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
         'j': jz, 'ji': ji, 'n': nota, 'na': float(c['nota_antiga']), 'inc': inc,
         'rx': [rr.get('passados'), rr.get('total')] if rr else None}
    g = a.get('regra_excepcional_grok_4_7_high')
    if g:
        assert me == 'grok-4.7-high'
        o['g'] = [g['nota_base'], g['fator'], g['regra']]
    X.append(o)
assert len(X) == 528, len(X)

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

g = C.defaultdict(list)
for x in X:
    if x['r'] == 1:
        g[f"{x['m']}-{x['x']}"].append(x)
nova = {}
for me, rs in g.items():
    assert len(rs) == 30, (me, len(rs))
    nova[me] = m2([r['n'] for r in rs])
    assert [nova[me], m2([r['na'] for r in rs])] == ref[me][:2], me
ordem = sorted(nova, key=lambda k: -nova[k])
assert [ref[k][2] for k in ordem] == list(range(1, 17)), ordem
emp_de = {f"{x['m']}-{x['x']}": x['e'] for x in X}

B7 = 'resultados/_avaliador/cenario_7min/'
resumo = json.load(open(B7 + 'resumo_7min.json'))
A1 = {(f"{x['m']}-{x['x']}", x['t']): x for x in X if x['r'] == 1}
XB = []
for l in csv.DictReader(open(B7 + 'notas_7min.csv', newline='')):
    me, t = l['combo'], l['tarefa']
    a = A1.get((me, t))
    if a is None or a['e'] != l['empresa']:
        falha(f'{me}/{t} sem par no Ranking A')
    o = {k: a[k] for k in ('e', 'm', 'x', 't', 'r', 's', 'd', 'p', 'tp', 'tt', 'rb', 'j', 'ji')}
    rf = l['refeita'] == 'True'
    if rf:
        f = f"resultados/{a['e']}/{me}/{t}/run-1/avaliacao_avaliador_7min.json"
        b = json.load(open(f))
        jz, ji = juizes(b)
        o.update(s=b['status'], d=round(b['duracao_agente_s'], 1), p=b['pct_testes'], tp=b['testes_passados'],
                 tt=b['testes_total'], rb=b['rubrica_media_10'], j=jz, ji=ji)
        if abs(b['nota_final_10'] - float(l['nota_ii'])) > 1e-9:
            falha(f'{f}: nota ≠ nota_ii do CSV')
    ni, nii = float(l['nota_i']), float(l['nota_ii'])
    if ni != (0.0 if o['s'] == 'timeout' else nii):
        falha(f'{me}/{t}: nota_i ≠ regra timeout = 0')
    if abs(round(0.7 * o['p'] / 10 + 0.3 * o['rb'], 2) - nii) > 1e-9:
        falha(f'{me}/{t}: nota_ii ≠ fórmula')
    o.update(ni=ni, nii=nii, rf=int(rf))
    XB.append(o)
if len(XB) != 360:
    falha(f'{len(XB)} execuções no Ranking B')
gB = C.defaultdict(list)
for x in XB:
    gB[f"{x['m']}-{x['x']}"].append(x)
base_de = lambda m: next(p for p in m.split('-') if p.isalpha() and p not in ('claude', 'gpt', 'gemini'))
TOL = 0.005 + 1e-9
refB, refBhm = {}, {}
for v, fld in (('nota_i', 'ni'), ('nota_ii', 'nii')):
    med = {me: S.mean(r[fld] for r in rs) for me, rs in gB.items()}
    for me in med:
        if abs(med[me] - resumo['res'][me][v]) > TOL:
            falha(f'{v} {me} ≠ resumo_7min.json')
    ordB = sorted(med, key=lambda k: -med[k])
    if {me: i for i, me in enumerate(ordB, 1)} != resumo['pos'][v]:
        falha(f'posições {v} ≠ resumo_7min.json')
    for me, i in resumo['pos'][v].items():
        refB.setdefault(me, {})[v] = [med[me], i]
    for m in sorted({gB[me][0]['m'] for me in gB}):
        d = med[m + '-high'] - med[m + '-medium']
        if abs(d - resumo['hm'][base_de(m)][v]) > TOL:
            falha(f'high−medium {m} {v} ≠ resumo_7min.json')
        refBhm.setdefault(m, {})[v] = d
if 'SEM DEFEITO NA TAREFA' not in ler('resultados/_avaliador/analise_10_ambigua_claude.md'):
    falha('10-ambigua: análise não valida a tarefa')


def md(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', s)


rodada = ler('resultados/RODADA.md')
regras = [md(l[2:].strip()) for l in rodada.split('## Regras específicas', 1)[1].split('##')[0].splitlines()
          if l.startswith('- ')]
metodo = [md(l[2:].strip()) for l in rel.split('## Metodologia', 1)[1].split('##')[0].splitlines()
          if l.startswith('- ')]


# ======================================================================== bloco v3
def run_v3(a, b=None):
    """Execução da rodada v3 no formato do bloco dados-v3 (o mesmo das execuções da Rodada 1)."""
    jz, ji = juizes(a)
    o = {'m': a['modelo'], 'x': a['esforco'], 't': a['tarefa'], 's': a['status'],
         'd': round(a['duracao_agente_s'], 1), 'p': a['pct_testes'], 'tp': a['testes_passados'],
         'tt': a['testes_total'], 'rb': a['rubrica_media_10'], 'j': jz, 'ji': ji,
         'n': a['nota_final_10'] if a['nota_final_10'] is not None else 0.0}
    return o


def placeholder(motivo):
    return {'status': PLACEHOLDER, 'motivo': motivo, 'modelos': MODELOS_V3, 'runsA': [], 'runsB': []}


def v3_de_pasta(raiz):
    runsA, runsB, faltaB = [], [], []
    for me in MODELOS_V3:
        fs = sorted(glob.glob(f'{raiz}/gemini/{me}/*/run-1/avaliacao_avaliador.json'))
        if not fs:
            return placeholder(f'nenhuma avaliação encontrada em {raiz}/gemini/{me}/')
        if len(fs) != 30:
            falha(f'v3 {me}: {len(fs)} tarefas avaliadas (esperado 30)')
        for f in fs:
            a = json.load(open(f))
            if a['tarefa'].endswith('-gemini'):
                falha(f'v3 {me}: {a["tarefa"]} é tarefa do próprio Gemini')
            o = run_v3(a)
            runsA.append(o)
            ob = dict(o)
            f7 = f.replace('avaliacao_avaliador.json', 'avaliacao_avaliador_7min.json')
            if a['status'] == 'timeout':
                if not os.path.exists(f7):
                    faltaB.append(f7); continue
                b = run_v3(json.load(open(f7)))
                ob.update({k: b[k] for k in ('s', 'd', 'p', 'tp', 'tt', 'rb', 'j', 'ji')}, rf=1)
            else:
                ob['rf'] = 0
            ob['nii'] = round(0.7 * ob['p'] / 10 + 0.3 * ob['rb'], 2) if ob['rb'] is not None else 0.0
            ob['ni'] = 0.0 if ob['s'] == 'timeout' else ob['nii']
            runsB.append(ob)
    if faltaB:
        print(f'AVISO v3: {len(faltaB)} timeouts sem avaliacao_avaliador_7min.json → v3 sem prazo estendido')
        runsB = []
    return {'status': 'ok', 'fonte': raiz, 'modelos': MODELOS_V3, 'runsA': runsA, 'runsB': runsB}


def v3_mock():
    """QA: dados FALSOS (Argon → Hydrogen, Flash → Neon) só para testar o caminho de plugar."""
    ren = {'gemini-4-argon': 'gemini-4-hydrogen', 'gemini-3.8-flash': 'gemini-4-neon'}
    ra = [dict({k: x[k] for k in ('m', 'x', 't', 's', 'd', 'p', 'tp', 'tt', 'rb', 'j', 'ji', 'n')}, m=ren[x['m']])
          for x in X if x['r'] == 1 and x['m'] in ren]
    rb = [dict({k: x[k] for k in ('m', 'x', 't', 's', 'd', 'p', 'tp', 'tt', 'rb', 'j', 'ji', 'ni', 'nii', 'rf')}, m=ren[x['m']])
          for x in XB if x['m'] in ren]
    return {'status': 'MOCK (QA) — dados falsos, cópia renomeada do Argon/Flash', 'modelos': MODELOS_V3,
            'runsA': ra, 'runsB': rb}


if ARGS.mock:
    V3 = v3_mock()
elif ARGS.v3_json:
    V3 = json.load(open(ARGS.v3_json))
else:
    V3 = v3_de_pasta(ARGS.v3_dir)
for k in ('status', 'modelos', 'runsA', 'runsB'):
    if k not in V3:
        falha(f'bloco v3 sem o campo "{k}"')

# ======================================================================== fontes e HTML
UNI = ('U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201D,U+2022,U+2026,U+2190-2194,U+2212,U+2248,U+2264-2265,'
       'U+25AE-25AF,U+25B2,U+25B6,U+25BC,U+25C0,U+00D7,U+03C3,U+2713-2714,U+2716')


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
dados = {'runs': X, 'runsB': XB, 'refB': refB, 'refBhm': refBhm, 'ref': ref, 'refEmp': ref_emp,
         'regras': regras, 'metodo': metodo, 'itens': ITENS, 'juiz_modelo': juiz_modelo}
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = open(os.path.join(AQUI, 'app.html')).read()
for marca in ('/*__FONTES__*/', '__DADOS__', '__DADOS_V3__'):
    assert html.count(marca) == 1, marca
v3txt = js(V3) if V3['status'] != PLACEHOLDER else json.dumps(V3, ensure_ascii=False, indent=1)
html = html.replace('/*__FONTES__*/', fontes).replace('__DADOS__', js(dados)).replace('__DADOS_V3__', v3txt)
if ARGS.mock:
    os.makedirs(os.path.join(AQUI, 'qa', 'mock'), exist_ok=True)
    out = os.path.join(AQUI, 'qa', 'mock', 'index-mock.html')
else:
    out = os.path.join(AQUI, 'index.html')
open(out, 'w').write(html)
print(f'{os.path.relpath(out, RAIZ)}: {len(html)/1024:.0f} KB (Rodada 1 {len(js(dados))/1024:.0f} KB, '
      f'v3 {len(v3txt)/1024:.1f} KB, fontes {len(fontes)/1024:.0f} KB)')
print(f'Rodada 1: ranking A (16, com Grok) confere com RELATORIO_AVALIADOR.md; ranking B (12) com resumo_7min.json')
print(f'bloco v3: status = {V3["status"]!r}; execuções A = {len(V3["runsA"])}, B = {len(V3["runsB"])}'
      + (f' ({V3.get("motivo")})' if V3.get('motivo') else ''))
