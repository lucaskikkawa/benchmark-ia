"""Gera resultados/RODADA.md a partir de resultado.json + avaliacao.json (exclui piloto)."""
import json,glob,os,statistics as S,collections as C
R=[]
for f in glob.glob('resultados/[cg]*/*/*/run-*/resultado.json'):
    r=json.load(open(f));a=json.load(open(f.replace('resultado.json','avaliacao.json')))
    d=os.path.dirname(f)+'/codigo'
    py=[os.path.join(p,x) for p,_,fs in os.walk(d) for x in fs if x.endswith('.py')] if os.path.isdir(d) else []
    r['src']=sum(os.path.getsize(p) for p in py)
    r['rub']=a['rubrica_10'] or 0;r['jz']={k:v['rubrica_10'] for k,v in a['juizes'].items() if v.get('rubrica_10') is not None}
    r['obs']=a.get('obs',[]);r['me']=f"{r['modelo']}-{r['esforco']}";r['tipo']=r['tarefa'][:2]
    r['sem']=0.7*r['pct_passados']/10+0.3*r['rub']
    r['nota']=0 if r['status']=='timeout' else r['sem']
    R.append(r)
m=lambda x:S.mean(x) if x else 0
o=[f"# Rodada 1 — resultados\n\n{len(R)} execuções (fora piloto). Nota final (0–10) = 0,7×%testes/10 + 0,3×rubrica (média de 2 juízes neutros; se só 1 válido, a nota dele). **Nota** conta timeout como 0; **Nota s/ pen.** ignora a penalidade.\n",
"## Ranking modelo × esforço\n\n|#|Modelo|Nota|Nota s/ pen.|%testes|Rubrica|Tempo médio (s)|Timeouts|Erros|N|\n|-|-|-|-|-|-|-|-|-|-|"]
g=C.defaultdict(list)
for r in R:g[(r['empresa'],r['me'])].append(r)
rk=sorted(g.items(),key=lambda kv:-m([r['nota'] for r in kv[1]]))
for i,((e,me),rs) in enumerate(rk,1):
    o.append(f"|{i}|{me} ({e})|{m([r['nota'] for r in rs]):.2f}|{m([r['sem'] for r in rs]):.2f}|{m([r['pct_passados'] for r in rs]):.1f}|{m([r['rub'] for r in rs]):.2f}|{m([r['duracao_agente_s'] for r in rs]):.0f}|{sum(r['status']=='timeout' for r in rs)}|{sum(r['status']=='erro' for r in rs)}|{len(rs)}|")
emp=sorted({r['empresa'] for r in R});tipos=sorted({r['tarefa'][:-len(r['tarefa'].split('-')[-1])-1] for r in R})
o+=["\n## Tipo × empresa (nota com penalidade)\n","|Tipo|"+"|".join(emp)+"|","|-|"+"-|"*len(emp)]
for t in tipos:
    o.append(f"|{t}|"+"|".join(f"{m([r['nota'] for r in R if r['empresa']==e and r['tarefa'].startswith(t+'-')]):.2f}" for e in emp)+"|")
o+=["\n## Medium vs high\n","|Modelo|Medium|High|Δ|Tempo med/high (s)|","|-|-|-|-|-|"]
for mo in sorted({r['modelo'] for r in R}):
    a=[r for r in R if r['modelo']==mo and r['esforco']=='medium'];b=[r for r in R if r['modelo']==mo and r['esforco']=='high']
    if a and b:
        x,y=m([r['nota'] for r in a]),m([r['nota'] for r in b]);o.append(f"|{mo}|{x:.2f}|{y:.2f}|{y-x:+.2f}|{m([r['duracao_agente_s'] for r in a]):.0f}/{m([r['duracao_agente_s'] for r in b]):.0f}|")
o+=["\n## Consistência (04-dados-claude; Claude usa 04-dados-grok; runs 1–4)\n","|Modelo|Notas por run|Média|Desvio|","|-|-|-|-|"]
for (e,me),rs in sorted(g.items()):
    t='04-dados-grok' if e=='claude' else '04-dados-claude'
    c=sorted([r for r in rs if r['tarefa']==t],key=lambda r:r['run']);n=[r['nota'] for r in c]
    if len(n)>1:o.append(f"|{me}|{', '.join(f'{v:.1f}' for v in n)}|{m(n):.2f}|{S.pstdev(n):.2f}|")
o.append("\n## Tarefas em que todos tiraram 100% nos testes\n")
bt=C.defaultdict(list)
for r in R:bt[r['tarefa']].append(r['pct_passados'])
tod=[t for t,v in sorted(bt.items()) if all(p==100 for p in v)]
o.append(("- "+"\n- ".join(tod)) if tod else "Nenhuma — todas as tarefas derrubaram ao menos uma execução.")
quase=[(t,sum(p==100 for p in v),len(v)) for t,v in sorted(bt.items()) if sum(p==100 for p in v)/len(v)>=0.9 and t not in tod]
if quase:o.append("\nQuase (≥90% das execuções com 100%): "+", ".join(f"{t} ({a}/{b})" for t,a,b in quase))
dv=[abs(a-b) for r in R if len(r['jz'])==2 for a,b in [tuple(r['jz'].values())]]
um=sum(len(r['jz'])==1 for r in R)
o+=["\n## Divergência entre juízes\n",f"- Execuções com 2 juízes válidos: {len(dv)}; com só 1: {um}; com 0: {sum(len(r['jz'])==0 for r in R)}." + " (sem juiz válido → rubrica 0)",
f"- |diferença| média: {m(dv):.2f} pts (de 10); mediana {S.median(dv) if dv else 0:.2f}; >3 pts: {sum(d>3 for d in dv)}."]
fal=C.Counter()
for r in R:
    for x in r['obs']:
        if 'falhou' in x:fal[' '.join(x.split()[:1])+' — '+x.split(':')[-1].strip()]+=1
o.append("- Falhas de juiz (tentativas): "+"; ".join(f"{k}: {v}" for k,v in fal.most_common()))
ju=C.defaultdict(list)
for r in R:
    for k,v in r['jz'].items():ju[k].append(v)
o.append("- Média dada por juiz: "+", ".join(f"{k} {m(v):.2f} (n={len(v)})" for k,v in sorted(ju.items())))
z=[r for r in R if 0 in r['jz'].values()];zc=C.Counter((r['status'],'código vazio' if r['src']==0 else 'código parcial') for r in z)
o+=["\n## Casos com rubrica 0,0 de algum juiz\n",f"{len(z)} execuções. Todas são timeout ou erro do agente — nenhuma com status ok: "+", ".join(f"{a}/{b}: {n}" for (a,b),n in zc.most_common())+".",
"Ou seja, o 0 é o juiz avaliando solução vazia/incompleta, não falha do juiz. As falhas reais de juiz (JSON inválido, sobretudo do Grok build-fast e também do Claude Haiku; timeouts do Gemini Flash) aparecem como 'só 1 juiz válido' e são cobertas pelo fallback.",
"\n|Modelo|Rubrica 0|","|-|-|"]
for k,v in C.Counter(r['me'] for r in z).most_common():o.append(f"|{k}|{v}|")
o+=["\n## Mutation score (tipo 08)\n","Não foi calculado com mutmut na rodada. O tipo 08 mede a qualidade dos testes escritos pelo agente via testes ocultos que rodam a suíte contra mutantes pré-definidos (ex.: 14 mutantes em 08-testes-claude); o %testes nesse tipo funciona como proxy de mutation score."]
open('resultados/RODADA.md','w').write("\n".join(o)+"\n")
