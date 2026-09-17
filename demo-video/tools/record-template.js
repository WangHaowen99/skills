// 录制脚本模板。复制到 ~/.playwright-mcp/<名字>.js，改「登录与打开」和「镜头」两段，
// 再用 browser_run_code_unsafe({ filename }) 跑。返回的 marks / rects 直接填进 cue。
//
// 约定：一次 run 录一段连续视频，里面顺序拍若干镜头；marks 记下每镜在这段录像里的
// 毫秒区间，rects 记下当场量到的包围盒（0~1 相对值）。不要事后目测框位置。
async (page) => {
  const ROOT = process.env.DEMO_VIDEO_ROOT || '/tmp/demo-video';
  const browser = page.context().browser();
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 810 }, deviceScaleFactor: 2,
    // 改成 <DEMO_VIDEO_ROOT>/vid/<本轮编号>；每轮录制单独一个目录，不要混写
    recordVideo: { dir: `${ROOT}/vid/r01`, size: { width: 2880, height: 1620 } },
  });
  const p = await ctx.newPage();
  const M = {}, R = {}; const t0 = Date.now(); const at = () => Date.now() - t0;
  const W = 1440, H = 810;

  // 每镜需要的秒数 = 配音时长 + 0.3。配音先生成，这里照抄，别拍脑袋。
  const NEED = { 'x-0': 0 };

  const norm = r => r && [+(r.x / W).toFixed(5), +(r.y / H).toFixed(5),
                          +(r.width / W).toFixed(5), +(r.height / H).toFixed(5)];

  // ---- 镜头计时 ----
  const start = (id) => { M[id] = [at()]; };
  const holdTo = async (id) => {
    const left = NEED[id] - 0.25 - (at() - M[id][0]) / 1000;
    if (left > 0.05) await p.waitForTimeout(left * 1000);
    await p.waitForTimeout(250);
    M[id].push(at());
  };

  // ---- 滚动：逐帧写 scrollTop ----
  // mouse.wheel 录不出连续位移，只会留下几次瞬移，见 PITFALLS。
  const pickScroller = (xMin, xMax) => p.evaluate(([a, b]) => {
    const cands = [...document.querySelectorAll('*')].filter(e => {
      const r = e.getBoundingClientRect();
      return e.scrollHeight > e.clientHeight + 40 && r.width > 200 && r.height > 200
          && r.x >= a && r.x <= b;
    });
    window.__sc = cands.sort((x, y) => y.clientHeight - x.clientHeight)[0] || null;
    return !!window.__sc;
  }, [xMin, xMax]);

  const anchorTop = (src) => p.evaluate((s) => {
    const sc = window.__sc; if (!sc) return null;
    const rx = new RegExp(s);
    const hit = [...sc.querySelectorAll('*')]
      .filter(e => e.children.length === 0 && rx.test(e.textContent || ''))[0];
    if (!hit) return null;
    return sc.scrollTop + hit.getBoundingClientRect().top - sc.getBoundingClientRect().top;
  }, src);

  const scrollRamp = async (to, secs) => {
    const n = Math.max(1, Math.round(secs * 1000 / 40));
    const from = await p.evaluate(() => (window.__sc ? window.__sc.scrollTop : 0));
    for (let i = 1; i <= n; i++) {
      const u = i / n, e = u * u * (3 - 2 * u);      // 两头缓、中间快
      await p.evaluate((v) => { if (window.__sc) window.__sc.scrollTop = v; },
                       from + (to - from) * e);
      await p.waitForTimeout(40);
    }
  };

  // 滚到某段文字附近：先量它离容器顶多远，再匀速滚过去
  const scrollToText = async (src, offsetFromTop, secs) => {
    const t = await anchorTop(src);
    if (t !== null) await scrollRamp(Math.max(0, t - offsetFromTop), secs);
    return t !== null;
  };

  // ---- 量包围盒 ----
  // 框住一组文字：给匹配规则，取它们在视口里的并集。maxBot 留出字幕带，
  // 字幕压住的框等于没画（底部约 0.855 以下、横向 0.16~0.85 是字幕区）。
  const boxOfText = (src, opts = {}) => p.evaluate(([s, o]) => {
    const rx = new RegExp(s);
    const rs = [...document.querySelectorAll('h1,h2,h3,h4,p,li,div,span')]
      .filter(e => e.children.length <= (o.maxKids ?? 3) && rx.test((e.textContent || '').trim()))
      .map(e => e.getBoundingClientRect())
      .filter(r => r.x >= (o.xMin ?? 0) && r.x <= (o.xMax ?? 99999)
                && r.width > (o.minW ?? 80)
                && r.top > (o.minTop ?? 100) && r.bottom < (o.maxBot ?? 690));
    if (!rs.length) return null;
    const pad = o.pad ?? 8;
    const x0 = Math.min(...rs.map(r => r.x)) - pad, y0 = Math.min(...rs.map(r => r.y)) - pad;
    return { x: x0, y: y0, width: Math.max(...rs.map(r => r.right)) + pad - x0,
             height: Math.max(...rs.map(r => r.bottom)) + pad - y0 };
  }, [src, opts]).then(norm);

  // 框住一组按钮（按钮文字精确匹配）
  const boxOfButtons = (names, pad = 6) => p.evaluate(([ns, q]) => {
    const rs = [...document.querySelectorAll('button')]
      .filter(b => ns.includes((b.textContent || '').trim()))
      .map(b => b.getBoundingClientRect()).filter(r => r.width > 10);
    if (!rs.length) return null;
    const x0 = Math.min(...rs.map(r => r.x)) - q, y0 = Math.min(...rs.map(r => r.y)) - q;
    return { x: x0, y: y0, width: Math.max(...rs.map(r => r.right)) + q - x0,
             height: Math.max(...rs.map(r => r.bottom)) + q - y0 };
  }, [names, pad]).then(norm);

  // ---- 交互 ----
  // 自定义样式的控件常常过不了 Playwright 的可点性检查；鼠标只负责移过去，
  // 真正的触发在页面内做，观众看到的仍是「移过去点一下」。
  const clickText = async (re, x, y) => {
    if (x != null) {
      for (let i = 0; i <= 12; i++) { await p.mouse.move(x - 70 + 70 * i / 12, y); await p.waitForTimeout(28); }
    }
    return p.evaluate((s) => {
      const rx = new RegExp(s);
      const b = [...document.querySelectorAll('button,a,[role=button],label')]
        .find(e => rx.test((e.textContent || '').trim()) && !e.disabled);
      if (b) { b.click(); return true; }
      return false;
    }, re);
  };

  // 往输入框里逐字打：按占位符认，页面上常常不止一个 textarea
  const typeInto = async (placeholderRe, text, perChar = 110) => {
    const el = await p.evaluateHandle((s) => {
      const rx = new RegExp(s);
      const tas = [...document.querySelectorAll('textarea,input[type=text]')];
      return tas.find(t => rx.test(t.placeholder || ''))
        || tas.sort((a, b) => b.getBoundingClientRect().y - a.getBoundingClientRect().y)[0];
    }, placeholderRe).then(h => h.asElement());
    if (!el) return false;
    await el.click();
    await p.waitForTimeout(300);
    for (const ch of text) { await p.keyboard.type(ch); await p.waitForTimeout(perChar); }
    return true;
  };

  // ---- WebGL 图谱（需要按你的实现适配）----
  // 图是 canvas 画的，DOM 里点不到节点，只能问渲染运行时要坐标。
  // 下面这版是从 React fiber 往上找、认 { positions: Map, getViewport(), nodeById: Map }
  // 这组接口——**这是某一类实现的形状，不是通用协议**。换个图库（cytoscape、sigma、
  // 自研 renderer）要改的就是「怎么拿到运行时」和「节点坐标叫什么」这两处，
  // 外面的 clickAt 和缩放不用动。摸不到就返回 null，调用方自己兜底。
  const graphNode = (pick = 'degree') => p.evaluate((mode) => {
    const canvases = [...document.querySelectorAll('canvas')]
      .map(c => ({ c, a: c.getBoundingClientRect().width * c.getBoundingClientRect().height }))
      .sort((x, y) => y.a - x.a).map(x => x.c);     // 小地图也是 canvas，按面积挑最大的
    let rt = null, canvas = null;
    for (const cv of canvases) {
      for (const from of [cv, cv.parentElement]) {
        if (rt || !from) break;
        let f = null;
        for (const k in from) if (k.startsWith('__reactFiber$')) f = from[k];
        let d = 0;
        while (f && !rt && d < 40) {
          let h = f.memoizedState, g = 0;
          while (h && !rt && g < 60) {
            const v = h.memoizedState;
            if (v && typeof v === 'object' && v.current && v.current.positions
                && typeof v.current.getViewport === 'function') rt = v.current;
            h = h.next; g++;
          }
          f = f.return; d++;
        }
      }
      if (rt) { canvas = cv; break; }
    }
    if (!rt || !canvas) return null;
    const vp = rt.getViewport(), box = canvas.getBoundingClientRect();
    const cands = [...rt.nodeById.values()]
      .filter(n => rt.positions.get(n.id))
      .map(n => {
        const q = rt.positions.get(n.id);
        return { id: n.id, x: box.left + q.x * vp.zoom + vp.x,
                 y: box.top + q.y * vp.zoom + vp.y, degree: n.degree || 0 };
      })
      .filter(n => n.x > box.left + 90 && n.x < box.right - 90
                && n.y > box.top + 90 && n.y < box.bottom - 90);
    if (mode === 'degree') cands.sort((a, b) => b.degree - a.degree);
    return cands[0] || null;
  }, pick);

  const clickAt = async (pt, approach = 170) => {
    const sx = pt.x - approach, sy = pt.y - approach * 0.65;
    for (let i = 0; i <= 22; i++) {
      await p.mouse.move(sx + (pt.x - sx) * i / 22, sy + (pt.y - sy) * i / 22);
      await p.waitForTimeout(28);
    }
    await p.waitForTimeout(400);
    await p.mouse.click(pt.x, pt.y);
  };

  // 图谱缩放：滚轮作用在 canvas 上是它自己处理的，这条路录出来是连续的。
  // 负值推近、正值拉远。
  const zoom = async (dy, secs, x = 700, y = 460) => {
    const deadline = Date.now() + secs * 1000;
    while (Date.now() < deadline) {
      await p.mouse.move(x, y);
      await p.mouse.wheel(0, dy);
      await p.waitForTimeout(30);
    }
  };

  // ================= 登录与打开 =================
  // 用环境自己的方式登录；不要把地址和口令写进这个模板。
  await p.goto(process.env.DEMO_URL || 'about:blank', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3000);

  // 页面还在加载时开拍会录到骨架屏或空画布。填上本产品的加载提示文案，
  // 等它消失再开始；没有这类文案就把 LOADING_TEXT 置空，只靠下面的定时等待。
  const LOADING_TEXT = process.env.DEMO_LOADING_TEXT || '';
  if (LOADING_TEXT) {
    await p.waitForFunction((s) => !new RegExp(s).test(document.body.innerText),
                            LOADING_TEXT, { timeout: 60000 }).catch(() => {});
  }
  await p.waitForTimeout(6000);

  // ===================== 镜头 =====================
  // 每镜：先量框（rects），再 start(id) → 动作 → holdTo(id)。
  // 有滚动的镜头，框要在滚停之后量，并给 cue 配 win，让框只在停稳后出现。
  //
  // start('x-0');
  // await scrollToText('某段文字', 160, 1.8);
  // await p.waitForTimeout(400);
  // R['x-0'] = await boxOfText('^某条：');
  // await holdTo('x-0');

  await p.close(); await ctx.close();
  return JSON.stringify({ marks: M, rects: R }, null, 1);
}
