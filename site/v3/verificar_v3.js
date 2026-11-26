// Verifica site/v3/index.html (site 1.0) no Chrome headless, em desktop (1280×800) e celular (390×844):
// todas as abas e sub-visões, números da Rodada 1 (sem Grok) contra RELATORIO_AVALIADOR.md e resumo_7min.json,
// bloco v3 com os resultados oficiais e, no mock (site/v3/qa/mock/index-mock.html), o caminho de plugar.
// Zero erros/avisos de console, zero requisições externas, sem rolagem horizontal. Prints em site/v3/qa/.
// Uso: python3 site/v3/build_v3.py && python3 site/v3/build_v3.py --mock && node site/v3/verificar_v3.js
const { chromium } = require('/node_modules/playwright-core');
const path = require('path');
const fs = require('fs');
const DIR = __dirname, QA = path.join(DIR, 'qa');
const RESUMO = JSON.parse(fs.readFileSync(path.join(DIR, '../../resultados/_avaliador/cenario_7min/resumo_7min.json'), 'utf8'));
const INDEX = 'file://' + path.join(DIR, 'index.html'), MOCK = 'file://' + path.join(QA, 'mock', 'index-mock.html');
fs.mkdirSync(QA, { recursive: true });
const falhas = [];
const ok = (c, msg) => { if (!c) falhas.push(msg); console.log((c ? '✔ ' : '✖ ') + msg); };
const f2 = v => (Math.round(v * 100) / 100).toFixed(2).replace('.', ',');

// Rodada 1, prazo normal (RELATORIO_AVALIADOR.md sem as 4 versões do Grok)
const ESPERADO_A = [['claude-haiku-5-5-high', '9,75'], ['claude-opus-5-5-medium', '9,70'], ['claude-haiku-5-5-medium', '9,66'],
  ['claude-opus-5-5-high', '9,39'], ['gpt-6-luna-medium', '9,09'], ['gpt-6-luna-high', '9,00'], ['gpt-6.1-sol-medium', '8,79'],
  ['gpt-6.1-sol-high', '8,16'], ['gemini-4-argon-medium', '7,22'], ['gemini-4-argon-high', '6,96'],
  ['gemini-3.8-flash-medium', '2,85'], ['gemini-3.8-flash-high', '1,31']];
const ESPERADO_V3_A = [['claude-haiku-5-5-high', '9,75'], ['claude-opus-5-5-medium', '9,70'], ['claude-haiku-5-5-medium', '9,66'],
  ['gemini-4-hydrogen-medium', '9,53'], ['claude-opus-5-5-high', '9,39'], ['gemini-4-hydrogen-high', '9,29'],
  ['gpt-6-luna-medium', '9,09'], ['gpt-6-luna-high', '9,00'], ['gemini-4-neon-medium', '8,87'], ['gpt-6.1-sol-medium', '8,79'],
  ['gemini-4-neon-high', '8,18'], ['gpt-6.1-sol-high', '8,16']];
const ESPERADO_V3_B = [['claude-haiku-5-5-high', '9,75'], ['claude-opus-5-5-high', '9,71'], ['claude-opus-5-5-medium', '9,70'],
  ['claude-haiku-5-5-medium', '9,66'], ['gemini-4-hydrogen-medium', '9,53'], ['gpt-6.1-sol-medium', '9,41'],
  ['gpt-6.1-sol-high', '9,39'], ['gpt-6-luna-high', '9,29'], ['gemini-4-hydrogen-high', '9,29'], ['gemini-4-neon-medium', '9,20'],
  ['gpt-6-luna-medium', '9,09'], ['gemini-4-neon-high', '8,84']];
const ordB = Object.keys(RESUMO.pos.nota_i).sort((a, b) => RESUMO.pos.nota_i[a] - RESUMO.pos.nota_i[b]);
const V3M = ['gemini-4-hydrogen-medium', 'gemini-4-hydrogen-high', 'gemini-4-neon-medium', 'gemini-4-neon-high'];
// jargão proibido fora da aba Técnico (réplica do Opus, pedido 2) + Grok fora da disputa
const JARGAO = /nota_i|nota_ii|\bN ?=|\bn=|\.py\b|\.json\b|\.csv\b|_avaliador|run-\d|σ|Δ|rubrica/;

(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const erros = [];
  const nova = async (vp, url, rotulo) => {
    const ctx = await browser.newContext(vp.mobile
      ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true }
      : { viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();
    page.on('console', m => { if (['error', 'warning', 'assert'].includes(m.type())) erros.push(`${rotulo} ${m.type()}: ${m.text()}`); });
    page.on('pageerror', e => erros.push(`${rotulo} pageerror: ${e.message}`));
    page.on('request', r => { if (!/^(file|data|blob):/.test(r.url())) erros.push(`${rotulo} rede: ${r.url()}`); });
    await page.goto(url); await page.waitForTimeout(1200);
    return page;
  };

  for (const vp of [{ nome: 'desktop', w: 1280, mobile: false }, { nome: 'celular', w: 390, mobile: true }]) {
    console.log(`\n===== ${vp.nome} (${vp.w}px) =====`);
    const page = await nova(vp, INDEX, vp.nome);
    const toca = async sel => { await page.click(sel); await page.waitForTimeout(450); };
    const rank = () => page.$$eval('#lista .lr:not(.pend)', els => els.map(e => [e.dataset.me, e.querySelector('.sc b').textContent]));
    const pend = () => page.$$eval('#lista .lr.pend', els => els.map(e => e.dataset.me));
    // como no verificar_site.js: estica a janela até a altura da página, para a barra fixa ficar no fim do print
    const print = async (nome, pg = page) => {
      await pg.waitForTimeout(700);
      const h = await pg.evaluate(() => document.documentElement.scrollHeight), alt = vp.mobile ? 844 : 800;
      await pg.setViewportSize({ width: vp.w, height: h }); await pg.waitForTimeout(250);
      await pg.screenshot({ path: path.join(QA, `${vp.nome}-${nome}.png`) });
      await pg.setViewportSize({ width: vp.w, height: alt }); await pg.waitForTimeout(150);
    };
    const semRolagem = async onde => { const l = await page.evaluate(() => document.documentElement.scrollWidth); ok(l <= vp.w, `${onde}: sem rolagem horizontal (${l}px)`); };
    const textoAba = id => page.$eval(id, e => e.innerText);
    const limpo = async (id, onde, grokOk) => {
      // o Grok pode aparecer só como autor de tarefa ("escrita pelo Grok"), nunca como competidor
      const t = (await textoAba(id) + ' ' + await page.$eval('header', e => e.innerText)).replace(/escritas? pelo Grok/g, '');
      const j = t.match(JARGAO), g = !grokOk && /grok/i.test(t);
      ok(!j && !g, `${onde}: sem jargão técnico nem Grok` + (j ? ` (achou "${j[0]}")` : '') + (g ? ' (achou "Grok")' : ''));
    };
    const folha = async (sel, onde) => {
      await toca(sel);
      ok(await page.isVisible('#folha'), `${onde}: toque abre os detalhes`);
      await page.click('#folha .x'); await page.waitForTimeout(250);
      ok(!(await page.isVisible('#folha')), `${onde}: detalhes fecham`);
    };

    // ---- abertura: teste novo, prazo normal (manchete A)
    ok(await page.$$eval('#nav button', b => b.length) === 5, '5 botões na barra (Ranking · Comparar · Esforço · Tarefas · Mais)');
    ok(await page.getAttribute('#segTeste [data-t=v3]', 'aria-pressed') === 'true', 'abre no teste novo (v3)');
    ok(await page.getAttribute('#segPrazo [data-p=A]', 'aria-pressed') === 'true' && await page.getAttribute('#segPrazo [data-p=B]', 'aria-pressed') === 'false', 'abre no prazo normal (manchete A)');
    ok(!(await page.isVisible('#avisoPend')), 'sem aviso de rodada v3 aguardando');
    ok(!(await page.isVisible('#avisoMock')) && !(await page.isVisible('#avisoAlt')), 'sem aviso de mock nem de regras alteradas');
    const p0 = await pend();
    ok(p0.length === 0, 'ranking v3: zero linhas pendentes');
    await print('abertura');
    const rA = await rank();
    ok(JSON.stringify(rA) === JSON.stringify(ESPERADO_V3_A), 'ranking v3 A = RODADA_V3.md (12 versões e notas oficiais)');
    await limpo('#aba-ranking', 'ranking v3 A');
    await semRolagem('ranking v3 A');
    await print('ranking-v3-normal');
    const cardA = await page.textContent('#cardGem');
    ok(!cardA.includes('aguardando') && /Hydrogen/.test(cardA) && /9,53/.test(cardA) && /7,22/.test(cardA) && /1,31/.test(cardA), 'card Gemini antigo × novo preenchido no prazo A');

    // ---- v3 prazo estendido
    await toca('#segPrazo [data-p=B]');
    const r0 = await rank();
    ok(JSON.stringify(r0) === JSON.stringify(ESPERADO_V3_B), 'ranking v3 B = RODADA_V3.md (12 versões e notas oficiais)');
    ok(V3M.every(me => r0.some(([id]) => id === me)), 'ranking v3 B inclui Hydrogen e Neon');
    const cardB = await page.textContent('#cardGem');
    ok(!cardB.includes('aguardando') && /Hydrogen/.test(cardB) && /Neon/.test(cardB) && /9,53/.test(cardB) && /Argon|Flash/.test(cardB), 'card Gemini antigo × novo preenchido no prazo B');
    ok((await page.textContent('#seloContas')).includes('batem com o relatório'), 'selo "as contas batem" verde');
    await limpo('#aba-ranking', 'ranking v3');
    await semRolagem('ranking v3');
    await print('ranking-v3-estendido');
    // resumo de 3 frases
    await toca('#btResumo');
    ok(await page.$$eval('#resumo p', p => p.filter(x => x.offsetParent).length) === 3, 'resumo abre as 3 frases');
    await toca('#btResumo');
    // glossário
    await folha('#btAjuda', 'glossário "?"');
    await folha('#leadRank .termo', 'termo sublinhado (empate técnico)');
    // tabela
    await page.click('#aba-ranking details.vt summary'); await page.waitForTimeout(200);
    ok(await page.$$eval('#tabRank tbody tr', t => t.length) === 12 && (await page.$$eval('#tabRank tbody', e => e[0].innerText)).indexOf('aguardando') < 0, 'ver como tabela: 12 linhas sem aguardando');
    await page.click('#aba-ranking details.vt summary');

    await toca('#segPrazo [data-p=A]');

    // ---- Rodada 1, prazo normal e estendido
    await toca('#segTeste [data-t=r1]');
    ok(!(await page.isVisible('#avisoPend')) && !(await page.isVisible('#cardGem')), 'Rodada 1: sem aviso v3 nem card Gemini antigo × novo');
    ok(JSON.stringify(await rank()) === JSON.stringify(ESPERADO_A) && (await pend()).length === 0, 'Rodada 1 A: 12 versões = RELATORIO_AVALIADOR.md sem Grok');
    const emp = await page.$$eval('#empMed .df', e => e.map(x => x.innerText.replace(/\s+/g, ' ')).join(' | '));
    ok(/Claude.*9,62.*Codex.*8,76.*Gemini.*4,58/.test(emp), 'Rodada 1 A: médias por empresa 9,62 / 8,76 / 4,58 (método do RODADA.md)');
    await limpo('#aba-ranking', 'ranking Rodada 1 A');
    await print('ranking-r1-normal');
    await toca('#segPrazo [data-p=B]');
    const rB = await rank();
    ok(JSON.stringify(rB.map(x => x[0])) === JSON.stringify(ordB) && rB.every(([me, n]) => n === f2(RESUMO.res[me].nota_i)), 'Rodada 1 B: 12 versões, posições e notas = resumo_7min.json');
    ok(!rB.some(([me]) => me.startsWith('grok')), 'Rodada 1 B: sem Grok');
    const empB = await page.$$eval('#empMed .df', e => e.map(x => x.innerText.replace(/\s+/g, ' ')).join(' | '));
    ok(/Claude.*9,71.*Codex.*9,29.*Gemini.*7,63/.test(empB), 'Rodada 1 B: médias por empresa 9,71 / 9,29 / 7,63 (método do RODADA.md)');
    await print('ranking-r1-estendido');

    // ---- E se…? e aviso de regras alteradas
    await toca('#ese [data-k=testes]');
    ok(await page.isVisible('#avisoAlt'), 'E se (só testes): aviso "regras alteradas" aparece');
    ok(JSON.stringify(await rank()) !== JSON.stringify(rB), 'E se (só testes): ranking muda');
    ok((await page.textContent('#eseTxt')).length > 10, 'E se: frase explica o que mudou');
    await print('ranking-e-se');
    await toca('#btOficial');
    ok(!(await page.isVisible('#avisoAlt')) && JSON.stringify(await rank()) === JSON.stringify(rB), 'voltar ao oficial restaura o ranking');
    await toca('#ese [data-k=prazo]');
    ok(await page.getAttribute('#segPrazo [data-p=A]', 'aria-pressed') === 'true' && !(await page.isVisible('#avisoAlt')), 'E se (prazo): troca para o prazo normal, sem aviso');
    await toca('#ese [data-k=prazo]');
    await toca('#segTeste [data-t=v3]');

    // ---- linha do ranking leva ao Comparar
    await toca('#lista .lr:not(.pend)');
    ok(await page.isVisible('#aba-comparar'), 'tocar numa linha do ranking abre o Comparar');

    // ---- Comparar
    for (const t of ['v3', 'r1']) {
      await toca(`#segTeste [data-t=${t}]`);
      ok(await page.$$eval('#crit .cl', e => e.length) === 7, `comparar ${t}: lista de 7 critérios`);
      const opts = await page.$$eval('#selA option:not([disabled])', o => o.map(x => x.value));
      ok(opts.length === 12 && !opts.some(o => o.startsWith('grok')), `comparar ${t}: ${opts.length} versões no seletor, sem Grok`);
      ok(/de \d+/.test(await page.textContent('#pA')), `comparar ${t}: placar A/B/empate`);
      ok(/\d+ min|\d+ s/.test(await page.textContent('#tempoAB')), `comparar ${t}: tempo em min e s`);
      await limpo('#aba-comparar', `comparar ${t}`);
      await semRolagem(`comparar ${t}`);
      await print(`comparar-${t}`);
    }
    await page.selectOption('#selB', 'gemini-3.8-flash-high'); await page.waitForTimeout(400);
    ok((await page.textContent('#cartaB')).includes('Gemini 3.8 Flash'), 'comparar: trocar o modelo B pelo seletor');
    await folha('#difTipo .lin', 'comparar: diferença por tipo');

    // ---- Esforço
    await toca('#nav button[data-aba=esforco]');
    for (const [t, p] of [['r1', 'B'], ['r1', 'A'], ['v3', 'B']]) {
      await toca(`#segTeste [data-t=${t}]`); await toca(`#segPrazo [data-p=${p}]`);
      const c = await page.textContent('#conclusao');
      const nLin = await page.$$eval('#hm .lin', e => e.length);
      ok(nLin === (t === 'r1' ? 6 : 6), `esforço ${t}/${p}: ${nLin} linhas no gráfico high − medium`);
      if (t === 'r1' && p === 'B') {
        ok(c.includes('empata ou melhora um pouco no Claude e no Codex') && c.includes('Argon, o high fica atrás, a não ser que se conte') && c.includes('Flash, o high continua bem pior') && c.includes('piorava (mesmo que pouco) em 5 de 6'), 'esforço r1/B: conclusão da réplica (5 de 6 sem Grok)');
        const hm = await page.$$eval('#tabHm tbody tr', t => t.map(r => [r.children[0].textContent, r.children[3].textContent]));
        const BASE = { 'Claude Haiku 5.5': 'haiku', 'Claude Opus 5.5': 'opus', 'GPT-6 Luna': 'luna', 'GPT-6.1 Sol': 'sol', 'Gemini 4 Argon': 'argon', 'Gemini 3.8 Flash': 'flash' };
        ok(hm.length === 6 && hm.every(([m, d]) => d.startsWith((RESUMO.hm[BASE[m]].nota_i >= 0 ? '+' : '−') + f2(Math.abs(RESUMO.hm[BASE[m]].nota_i)))), 'esforço r1/B: high − medium = resumo_7min.json');
      }
      if (t === 'v3') {
        const linhas = await page.$$eval('#hm .lin', e => e.map(x => [x.dataset.m, x.getAttribute('aria-label')]));
        ok(linhas.length === 6 && ['gemini-4-hydrogen', 'gemini-4-neon'].every(id => linhas.some(([mid]) => mid === id)) && linhas.every(([, label]) => !/aguardando/i.test(label || '')), 'esforço v3: 6 linhas incluindo Hydrogen e Neon, sem aguardando');
      }
      await limpo('#aba-esforco', `esforço ${t}/${p}`);
      await semRolagem(`esforço ${t}/${p}`);
      await print(`esforco-${t}-${p === 'A' ? 'normal' : 'estendido'}`);
    }
    await folha('#hm .lin', 'esforço: gráfico high − medium');

    // ---- Tarefas (3 modos)
    await toca('#nav button[data-aba=tarefas]');
    for (const t of ['v3', 'r1']) {
      await toca(`#segTeste [data-t=${t}]`);
      for (const [m, n] of [['emp', 3], ['me', t === 'v3' ? 12 : 12], ['aut', 4]]) {
        await toca(`#modos [data-m=${m}]`);
        const cols = await page.$$eval('#mapa .ch', e => e.length);
        ok(cols === n, `tarefas ${t} modo ${m}: ${cols} colunas`);
        ok(await page.$$eval('#mapa .rl', e => e.length) === 10, `tarefas ${t} modo ${m}: 10 tipos`);
        await limpo('#aba-tarefas', `tarefas ${t} modo ${m}`, m === 'aut');
        await semRolagem(`tarefas ${t} modo ${m}`);
        await print(`tarefas-${t}-${m}`);
      }
      await toca('#modos [data-m=emp]');
    }
    await folha('#mapa .cel[data-t]', 'tarefas: célula do mapa');

    // ---- Mais: por que confiar, técnico, Grok
    await toca('#nav button[data-aba=mais]');
    await toca('#segSub [data-s=confiar]');
    ok(await page.$$eval('#sub-confiar .jz', e => e.length) === 4, 'por que confiar: 4 juízes');
    await folha('#sub-confiar .jz', 'por que confiar: juiz');
    await semRolagem('mais/confiar'); await print('mais-confiar');
    await toca('#segSub [data-s=tecnico]');
    const tecV3 = await page.textContent('#tecnico-v3');
    ok(await page.isVisible('#tecnico-v3') && /Status:\s*ok/i.test(tecV3) && /hydrogen/i.test(tecV3) && /neon/i.test(tecV3) && !/aguardando rodada v3/i.test(tecV3), 'técnico: bloco v3 com status ok e dados reais');
    ok((await page.$$eval('#sub-tecnico .ok-ref', e => e.length)) >= 2, 'técnico: conferências A e B verdes');
    await page.$eval('#slider', s => { s.value = 50; s.dispatchEvent(new Event('input', { bubbles: true })); }); await page.waitForTimeout(400);
    ok(await page.isVisible('#avisoAlt') && (await page.textContent('#pesoTxt')).includes('50%'), 'técnico: slider de peso muda as regras e mostra o aviso');
    await toca('#tgVies');
    ok(await page.getAttribute('#tgVies', 'aria-checked') === 'true', 'técnico: correção de viés liga');
    await toca('#btReset');
    ok(!(await page.isVisible('#avisoAlt')), 'técnico: padrão do relatório restaura');
    await semRolagem('mais/técnico'); await print('mais-tecnico');
    await toca('#segSub [data-s=grok]');
    const gk = await page.textContent('#sub-grok');
    ok(gk.includes('saiu da disputa') && gk.includes('juiz') && gk.includes('autor'), 'por que o Grok saiu: fora da disputa, continua autor e juiz');
    await semRolagem('mais/grok'); await print('mais-grok');
    // link "como isso é conferido →" leva ao técnico
    await toca('#nav button[data-aba=ranking]');
    await toca('#aba-ranking [data-tec=tecnico-conferencia]'); await page.waitForTimeout(600);
    ok(await page.isVisible('#tecnico-conferencia'), 'link do ranking abre a seção do técnico');

    // ---- hash: estado e links antigos
    ok(page.url().includes('t=v3') || page.url().includes('t=r1'), 'teste ativo no hash');
    const p2 = await nova(vp, INDEX + '#ranking&t=r1&p=A&a=grok-4.7-high&emp=grok&pg=0', vp.nome + '(hash)');
    ok(JSON.stringify(await p2.$$eval('#lista .lr:not(.pend)', els => els.map(e => [e.dataset.me, e.querySelector('.sc b').textContent]))) === JSON.stringify(ESPERADO_A), 'link antigo com Grok cai na vista oficial (Rodada 1 A)');
    await p2.close();
    const p3 = await nova(vp, INDEX + '#ranking&t=r1&p=B&w=100', vp.nome + '(hash w)');
    ok(await p3.isVisible('#avisoAlt'), 'link com regras alteradas (w=100) abre com aviso');
    await p3.close();
    await page.context().close();

    // ---- mock: o caminho de plugar os números do v3
    const pm = await nova(vp, MOCK, vp.nome + '(mock)');
    ok(await pm.isVisible('#avisoMock') && !(await pm.isVisible('#avisoPend')), 'mock: aviso de dados de teste, sem "aguardando"');
    const rm = await pm.$$eval('#lista .lr:not(.pend)', els => els.map(e => e.dataset.me));
    ok(rm.length === 12 && V3M.every(me => rm.includes(me)) && (await pm.$$eval('#lista .lr.pend', e => e.length)) === 0, 'mock: Neon e Hydrogen entram no ranking v3 (12 versões)');
    ok(!(await pm.textContent('#cardGem')).includes('aguardando'), 'mock: card Gemini antigo × novo preenchido');
    await print('mock-ranking', pm);
    await pm.click('#nav button[data-aba=esforco]'); await pm.waitForTimeout(600);
    ok(await pm.$$eval('#hm .lin', e => e.length) === 6, 'mock: esforço com Hydrogen e Neon');
    await print('mock-esforco', pm);
    await pm.context().close();
  }

  // ---- movimento reduzido: sem animações
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
  const pr = await ctx.newPage();
  pr.on('pageerror', e => erros.push('reduced pageerror: ' + e.message));
  await pr.goto(INDEX); await pr.waitForTimeout(600);
  ok(await pr.evaluate(() => document.getAnimations().filter(a => a.playState === 'running').length) === 0, 'prefers-reduced-motion: nenhuma animação rodando');
  await ctx.close();

  ok(erros.length === 0, 'zero erros/avisos de console, pageerror e requisições externas' + (erros.length ? ': ' + erros.join(' | ') : ''));
  await browser.close();
  console.log(falhas.length ? `\n${falhas.length} FALHA(S)` : '\nTUDO OK');
  process.exit(falhas.length ? 1 : 0);
})();
