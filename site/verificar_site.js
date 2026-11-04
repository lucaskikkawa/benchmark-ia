// Verifica site/index.html (notas do Avaliador independente) em 390x844 (Chrome headless) e gera site/site-<aba>.png.
// Uso: node site/verificar_site.js
const { chromium } = require('/node_modules/playwright-core');
const path = require('path');
const DIR = __dirname;
const falhas = [];
const ok = (c, msg) => { if (!c) falhas.push(msg); console.log((c ? '✔ ' : '✖ ') + msg); };

(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const erros = [];
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning' || m.type() === 'assert') erros.push(m.type() + ': ' + m.text()); });
  page.on('pageerror', e => erros.push('pageerror: ' + e.message));
  page.on('request', r => { if (!r.url().startsWith('file:') && !r.url().startsWith('data:') && !r.url().startsWith('blob:')) erros.push('rede: ' + r.url()); });
  await page.goto('file://' + path.join(DIR, 'index.html'));
  await page.waitForTimeout(1200);

  const rank = () => page.$$eval('#lista .lr:not(.oculto)', els => els.map(e => [e.dataset.me, e.querySelector('.sc b').textContent]));
  const print = async nome => {
    const h = await page.evaluate(() => document.documentElement.scrollHeight);
    await page.setViewportSize({ width: 390, height: h }); await page.waitForTimeout(250);
    await page.screenshot({ path: path.join(DIR, nome) });
    await page.setViewportSize({ width: 390, height: 844 }); await page.waitForTimeout(150);
  };
  const nota = async me => { await page.waitForTimeout(600); return Object.fromEntries(await rank())[me]; };
  const pos = (r, me) => r.findIndex(x => x[0] === me);

  // ---- ranking padrão = RELATORIO_AVALIADOR.md (N=30)
  const ESPERADO = [['claude-haiku-5-5-high', '9.75'], ['claude-opus-5-5-medium', '9.70'], ['claude-haiku-5-5-medium', '9.66'],
    ['claude-opus-5-5-high', '9.39'], ['gpt-6-luna-medium', '9.09'], ['gpt-6-luna-high', '9.00'], ['gpt-6.1-sol-medium', '8.79'],
    ['gpt-6.1-sol-high', '8.16'], ['grok-4.7-build-fast-medium', '7.68'], ['gemini-4-argon-medium', '7.22'], ['gemini-4-argon-high', '6.96'],
    ['grok-4.7-medium', '6.72'], ['grok-4.7-build-fast-high', '3.86'], ['grok-4.7-high', '3.83'], ['gemini-3.8-flash-medium', '2.85'],
    ['gemini-3.8-flash-high', '1.31']];
  const r0 = await rank();
  ok(r0.length === 16, '16 linhas no ranking');
  ok(JSON.stringify(r0) === JSON.stringify(ESPERADO), 'ranking padrão = RELATORIO_AVALIADOR.md' + (JSON.stringify(r0) === JSON.stringify(ESPERADO) ? '' : ': ' + JSON.stringify(r0)));
  ok((await page.textContent('#rodape')).includes('conferem com RELATORIO_AVALIADOR.md'), 'rodapé: confere com RELATORIO_AVALIADOR.md');
  const c = await page.$$eval('[data-n]', e => e.map(x => x.textContent));
  ok(c.join() === '480,120,48', 'contadores 480/120/48: ' + c);
  ok((await page.textContent('#seloGrok')) === '⚖️ ×0,7/×0,5', 'selo na linha do grok-4.7-high');
  ok(await page.$$eval('.selo', e => e.filter(x => x.closest('#lista')).length) === 1, 'só o grok-4.7-high tem selo');
  const gi = await page.textContent('#grokInfo');
  ok(gi.includes('3.83') && gi.includes('4.19') && gi.includes('13 execuções'), 'aviso do grok-4.7-high: 3.83 / 4.19 / 13 execuções');
  await print('site-ranking.png');

  // ---- toggle penalidades do grok
  await page.tap('#tgGrok');
  ok(await nota('grok-4.7-high') === '4.19', 'sem penalidades: grok-4.7-high 4.19');
  const r1 = await rank();
  ok(pos(r1, 'grok-4.7-high') === 12 && pos(r1, 'grok-4.7-build-fast-high') === 13, 'sem penalidades: grok-4.7-high passa grok-4.7-build-fast-high (13º)');
  ok(r1.filter(x => x[0] !== 'grok-4.7-high').every(x => x[1] === Object.fromEntries(r0)[x[0]]), 'toggle só mexe no grok-4.7-high');
  ok((await page.textContent('#seloGrok')) === '⚖️ sem pen.', 'selo indica sem penalidade');
  ok((await page.textContent('#tagPadrao')) === 'seu ranking', 'selo "seu ranking"');
  await page.tap('#tgGrok'); await page.waitForTimeout(500);
  ok(JSON.stringify(await rank()) === JSON.stringify(r0), 'religar volta ao padrão');

  // ---- slider de pesos (CSV tem %testes e rubrica separados)
  await page.$eval('#slider', s => { s.value = 100; s.dispatchEvent(new Event('input', { bubbles: true })); });
  ok(await nota('claude-opus-5-5-medium') === '10.00' && await nota('claude-haiku-5-5-high') === '10.00', 'slider 100%: opus-medium e haiku-high 10.00');
  ok((await page.textContent('#pesoTxt')).includes('100% testes'), 'rótulo do slider atualiza');
  await page.$eval('#slider', s => { s.value = 0; s.dispatchEvent(new Event('input', { bubbles: true })); });
  ok(await nota('claude-haiku-5-5-high') === '9.18', 'slider 0%: haiku-high 9.18 (= rubrica média)');
  ok(await nota('grok-4.7-high') === '3.51', 'slider 0%: grok-4.7-high 3.51');
  await page.tap('#btReset'); await page.waitForTimeout(500);
  ok(JSON.stringify(await rank()) === JSON.stringify(r0), 'reset volta ao padrão');
  // ---- nota antiga
  await page.tap('#tgAnt'); await page.waitForTimeout(400);
  ok((await page.textContent('#lista [data-me="grok-4.7-high"] .an')) === 'antes 2.26', 'nota antiga do grok-4.7-high: 2.26');
  ok(await page.isVisible('#lista [data-me="grok-4.7-high"] .fant'), 'marcador fantasma visível');
  await page.tap('#tgAnt'); await page.waitForTimeout(300);
  // ---- viés
  await page.tap('#btVies'); await page.waitForTimeout(600);
  const rv = await rank();
  ok(JSON.stringify(rv) !== JSON.stringify(r0), 'corrigir viés muda as notas');
  await page.tap('#btReset'); await page.waitForTimeout(500);
  // aviso do grok leva às letras miúdas
  await page.tap('#grokInfo'); await page.waitForTimeout(700);
  ok(await page.$eval('#regrasGrok', d => d.open) && (await page.textContent('#regrasGrok')).includes('somente para o grok-4.7-high'), 'aviso abre as regras do grok nas letras miúdas');
  ok(await page.$$eval('#regrasGrok tbody tr', t => t.length) >= 13, 'tabela das 13 execuções com regra especial');

  // ---- abas
  for (const aba of ['comparar', 'esforco', 'tarefas', 'juizes']) {
    await page.tap(`#nav button[data-aba=${aba}]`);
    await page.waitForTimeout(500);
    ok(await page.isVisible('#aba-' + aba), 'aba ' + aba + ' visível');
    const larg = await page.evaluate(() => document.documentElement.scrollWidth);
    ok(larg <= 390, `aba ${aba}: sem rolagem horizontal (${larg}px)`);
    await print(`site-${aba}.png`);
  }
  ok(await page.$$eval('#nav button', b => b.length) === 5, '5 abas');
  ok((await page.$$eval('#aba-tarefas .rl', e => e.map(x => x.textContent)))[0] === '01 função', 'tipos em ordem 01..10');
  // comparar
  await page.tap('#nav button[data-aba=comparar]'); await page.waitForTimeout(300);
  ok(await page.$$eval('#radar polygon', p => p.length) >= 6, 'radar desenhado');
  await page.selectOption('#selB', 'grok-4.7-high'); await page.waitForTimeout(300);
  const v1 = await page.textContent('#vence');
  await page.tap('#radar .ax'); ok((await page.textContent('#readout')).includes('Legível'), 'toque no eixo do radar mostra valores');
  await page.tap('#esp .esp'); await page.waitForTimeout(300);
  ok(await page.isVisible('#folha') && (await page.$$eval('#folhaC tr', t => t.length)) > 2, 'toque na barra abre execuções');
  await page.tap('#folha .x');
  // esforço
  await page.tap('#nav button[data-aba=esforco]'); await page.waitForTimeout(300);
  const ve = await page.textContent('#veredito');
  ok(ve.includes('High piorou em 7 de 8'), 'veredito: 7 de 8');
  ok(ve.includes('grok-4.7-build-fast, de 7.68 para 3.86'), 'maior queda grok-4.7-build-fast 7.68 → 3.86');
  const td = await page.textContent('#tabDumb');
  ok(td.includes('-3.82') && td.includes('+0.09') && td.includes('-2.89'), 'Δ: build-fast -3.82, haiku +0.09, grok-4.7 -2.89');
  await page.tap('#dumb .lin'); await page.waitForTimeout(300);
  ok(await page.isVisible('#folha'), 'toque no halter abre detalhes'); await page.tap('#folha .x');
  // tarefas
  await page.tap('#nav button[data-aba=tarefas]'); await page.waitForTimeout(300);
  const hm = await page.textContent('#tabHm');
  ok(hm.includes('9.87') && hm.includes('0.82') && hm.includes('9.39'), 'heatmap: 08 claude 9.87, gemini 0.82, 10 codex 9.39');
  await page.tap('#modos button[data-m=me]'); await page.waitForTimeout(300);
  ok(await page.$$eval('#hm .ch', e => e.length) === 16, 'modo modelo×esforço: 16 colunas');
  await page.tap('#modos button[data-m=aut]'); await page.waitForTimeout(300);
  ok(await page.$$eval('#hm .ch', e => e.length) === 4, 'modo autora: 4 colunas');
  await page.tap('#modos button[data-m=emp]'); await page.waitForTimeout(300);
  await page.tap('#hm .cel[data-t]'); await page.waitForTimeout(300);
  ok(await page.isVisible('#folha'), 'toque na célula abre execuções'); await page.tap('#folha .x');
  // avaliador
  await page.tap('#nav button[data-aba=juizes]'); await page.waitForTimeout(300);
  ok((await page.textContent('#nav button[data-aba=juizes]')).includes('Avaliador'), 'aba renomeada para Avaliador');
  ok((await page.textContent('#troca')).includes('Avaliador independente'), 'explica a troca juízes → Avaliador');
  const tr = await page.textContent('#trib');
  ok(['8.28', '8.40', '8.34', '8.60', 'n=175', 'n=174', 'n=232', 'n=207'].every(s => tr.includes(s)), 'médias dos juízes do Avaliador');
  ok((await page.textContent('#nPares')) === '394 execuções', '394 pares');
  const dt = await page.textContent('#dispTxt');
  ok(dt.includes('0.63') && dt.includes(' 3 casos'), 'divergência 0.63 e 3 casos');
  const at = await page.textContent('#antTxt');
  ok(at.includes('grok-4.7-high (2.26 → 3.83)') && at.includes('claude 9.62 → 9.62') && at.includes('codex 8.64 → 8.76') && at.includes('grok 5.14 → 5.52') && at.includes('gemini 4.61 → 4.58'), 'antiga × nova (modelo e empresa): ' + at);
  ok(await page.$$eval('#antNova .lin', e => e.length) === 16, 'gráfico antiga × nova com 16 linhas');
  ok((await page.textContent('#audit')).includes('528/528'), 'auditoria: 528/528 reexecutadas');
  await page.tap('#antNova .lin'); await page.waitForTimeout(300);
  ok(await page.isVisible('#folha'), 'toque em antiga × nova abre execuções'); await page.tap('#folha .x');
  await page.tap('#audit button.au'); await page.waitForTimeout(300);
  ok(await page.isVisible('#folha'), 'toque na auditoria abre execuções'); await page.tap('#folha .x');
  await page.tap('#disp .bo'); await page.waitForTimeout(300);
  ok(await page.isVisible('#folha'), 'toque na bolha abre execuções'); await page.tap('#folha .x');
  await page.tap('#tgVies'); await page.waitForTimeout(300);
  await page.tap('#nav button[data-aba=ranking]'); await page.waitForTimeout(600);
  ok(JSON.stringify(await rank()) !== JSON.stringify(r0), 'viés ligado na aba Avaliador muda o ranking');
  await page.tap('#btReset'); await page.waitForTimeout(400);
  // controles em outra aba (pill)
  await page.tap('#nav button[data-aba=esforco]'); await page.waitForTimeout(300);
  await page.tap('#pill'); await page.waitForTimeout(300);
  ok(await page.isVisible('#folha #tgGrok'), 'pill abre os controles em outra aba');
  await page.tap('#folha .x'); await page.waitForTimeout(200);
  ok(await page.$('#casa-controles #controles') !== null, 'controles voltam para o lugar');
  // hash
  await page.tap('#nav button[data-aba=ranking]'); await page.tap('#tgGrok'); await page.waitForTimeout(300);
  ok(page.url().includes('pg=0'), 'estado no hash');
  const p2 = await browser.newPage({ viewport: { width: 390, height: 844 } });
  p2.on('pageerror', e => erros.push('pageerror(p2): ' + e.message));
  p2.on('console', m => { if (m.type() === 'error' || m.type() === 'warning' || m.type() === 'assert') erros.push('p2 ' + m.type() + ': ' + m.text()); });
  await p2.goto('file://' + path.join(DIR, 'index.html') + '#ranking&w=70&pg=0');
  await p2.waitForTimeout(800);
  ok((await p2.$eval('#lista [data-me="grok-4.7-high"] .sc b', e => e.textContent)) === '4.19', 'link com #pg=0 abre sem penalidades do grok');

  ok(erros.length === 0, 'zero erros/avisos de console, pageerror e rede' + (erros.length ? ': ' + erros.join(' | ') : ''));
  console.log('(info) A × grok-4.7-high: A vence em ' + v1);
  await browser.close();
  console.log(falhas.length ? `\n${falhas.length} FALHA(S)` : '\nTUDO OK');
  process.exit(falhas.length ? 1 : 0);
})();
