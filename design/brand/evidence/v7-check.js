async(page)=>{
  const app=page.locator('#app-view'),nav=page.getByRole('navigation',{name:'示例 App 导航'}),phone=page.getByLabel('凑狸 App 交互方向示例');
  const results=[];const assert=(v,m)=>{if(!v)throw new Error(m);};
  await nav.getByRole('button',{name:'我的',exact:true}).click();await app.getByRole('button',{name:'收益明细 →',exact:true}).click();
  for(const [width,zoom,name] of [[390,100,'ledger-v7'],[320,200,'ledger-200pct-v7']]){
    await page.setViewportSize({width,height:900});await page.evaluate(zoom=>document.documentElement.style.fontSize=`${zoom}%`,zoom);
    const result=await page.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth,stack:[...state.navigation],text:document.querySelector('#app-view .order-card').textContent,groups:[...document.querySelectorAll('#app-view .order-card .money')].map(e=>({text:e.textContent,whiteSpace:getComputedStyle(e).whiteSpace,rects:e.getClientRects().length,width:e.getBoundingClientRect().width})),bad:[...document.querySelectorAll('#app-view *')].filter(e=>e.getClientRects().length&&!e.classList.contains('sr-only')&&e.clientWidth>0&&e.scrollWidth>e.clientWidth+1).map(e=>e.className)}));
    assert(result.viewport===result.scroll&&!result.bad.length,'no horizontal overflow');assert(result.text.includes('自购返利 +¥1.5')&&result.text.includes('昨天 14:00 · 示例流水（演示日期 2026-10-01）'),'visible wording unchanged');assert(JSON.stringify(result.stack)==='["me","ledger"]','same navigation');assert(result.groups.length===2&&result.groups.every(g=>g.whiteSpace==='nowrap'&&g.rects===1),'amount and date each occupy one unbroken rectangle');assert(result.groups[0].text==='+¥1.5'&&result.groups[1].text==='2026-10-01','exact unbroken groups');
    await phone.screenshot({path:`/tmp/couli-ui-review/${name}.png`});results.push({width,zoom,...result});
  }
  return {passed:results.length,results};
}
