async(page)=>{
 const app=page.locator('#app-view'),nav=page.getByRole('navigation',{name:'示例 App 导航'}),phone=page.getByLabel('凑狸 App 交互方向示例');
 const results=[];const assert=(v,m)=>{if(!v)throw new Error(m);};
 await nav.getByRole('button',{name:'我的',exact:true}).click();await app.getByRole('button',{name:'收益明细 →',exact:true}).click();
 for(const [width,zoom,name] of [[390,100,'ledger-v8'],[320,200,'ledger-200pct-v8']]){
  await page.setViewportSize({width,height:900});await page.evaluate(zoom=>document.documentElement.style.fontSize=`${zoom}%`,zoom);
  const button=app.getByRole('button',{name:'查看关联订单 →',exact:true});assert(await button.textContent()==='查看关联订单 →','exact visible text/name no new whitespace');
  const data=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,groups:[...document.querySelectorAll('#app-view .money')].map(e=>({text:e.textContent,whiteSpace:getComputedStyle(e).whiteSpace,rects:e.getClientRects().length,width:e.getBoundingClientRect().width})),bad:[...document.querySelectorAll('#app-view *')].filter(e=>e.getClientRects().length&&!e.classList.contains('sr-only')&&e.clientWidth>0&&e.scrollWidth>e.clientWidth+1).map(e=>e.className)}));
  assert(data.width===data.scroll&&!data.bad.length,'no horizontal overflow');assert(data.groups.length===3&&data.groups.every(x=>x.whiteSpace==='nowrap'&&x.rects===1),'all three groups unbroken');assert(JSON.stringify(data.groups.map(x=>x.text))==='["+¥1.5","2026-10-01","订单 →"]','three expected groups');
  await phone.screenshot({path:`/tmp/couli-ui-review/${name}.png`});
  await button.click();assert((await app.innerText()).includes('2026-09-30 14:00'),'correct linked settled order');await app.locator('.back-row [data-back]').click();assert(await app.getByRole('button',{name:'查看关联订单 →',exact:true}).isVisible(),'returns to ledger');assert(await page.evaluate(()=>JSON.stringify(state.navigation))==='["me","ledger"]','original ledger stack retained');results.push({width,zoom,...data,linkedOrderReturn:true});
 }
 return {passed:results.length,results};
}
