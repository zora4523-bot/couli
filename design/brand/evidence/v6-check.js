async(page)=>{
  const app=page.locator('#app-view'),nav=page.getByRole('navigation',{name:'示例 App 导航'}),phone=page.getByLabel('凑狸 App 交互方向示例');
  const assert=(ok,message)=>{if(!ok)throw new Error(message);};
  const expected='昨天 14:00 · 示例流水（演示日期 2026-10-01）';
  const results=[];
  const check=async(stack,label)=>{
    assert((await app.innerText()).includes(expected),`${label}: yesterday time and fixture date`);
    const actual=await page.evaluate(()=>({stack:[...state.navigation],width:innerWidth,scroll:document.documentElement.scrollWidth,bad:[...document.querySelectorAll('#app-view *')].filter(e=>e.getClientRects().length&&!e.classList.contains('sr-only')&&e.clientWidth>0&&e.scrollWidth>e.clientWidth+1).map(e=>e.className)}));
    assert(JSON.stringify(actual.stack)===JSON.stringify(stack),`${label}: source stack`);assert(actual.width===actual.scroll&&!actual.bad.length,`${label}: no overflow`);
    assert(await nav.getByRole('button',{name:'我的',exact:true}).getAttribute('aria-pressed')==='true',`${label}: me selected`);assert(await nav.locator('[aria-pressed="true"]').count()===1,`${label}: exactly one Tab`);results.push({label,...actual});
  };
  const me=async()=>nav.getByRole('button',{name:'我的',exact:true}).click();
  const ledger=async()=>app.getByRole('button',{name:'收益明细 →',exact:true}).click();
  const linked=async()=>{await app.getByRole('button',{name:'查看关联订单 →',exact:true}).click();assert((await app.locator('.timeline').innerText()).includes('2026-09-30 14:00'),'detail retains full timestamp');await app.locator('.back-row [data-back]').click();};
  await page.setViewportSize({width:390,height:844});await me();await ledger();await check(['me','ledger'],'390px from me');await phone.screenshot({path:'/tmp/couli-ui-review/ledger-v6.png'});await linked();await check(['me','ledger'],'linked order returns to me ledger');await app.locator('.back-row [data-back]').click();
  await app.getByRole('button',{name:'查看钱包',exact:true}).click();await ledger();await check(['me','wallet','ledger'],'390px from wallet');await linked();await check(['me','wallet','ledger'],'linked order returns to wallet ledger');await app.locator('.back-row [data-back]').click();assert((await app.innerText()).includes('冻结中'),'ledger returns original wallet');
  await nav.getByRole('button',{name:'订单',exact:true}).click();assert((await app.innerText()).includes('今天 09:00')&&(await app.innerText()).includes('京东 · 08-28'),'order list dates unchanged');
  await page.setViewportSize({width:320,height:900});await page.evaluate(()=>document.documentElement.style.fontSize='200%');await me();await ledger();await check(['me','ledger'],'320px 200% from me');await phone.screenshot({path:'/tmp/couli-ui-review/ledger-200pct-v6.png'});await linked();await check(['me','ledger'],'320px 200% linked return');await app.locator('.back-row [data-back]').click();await app.getByRole('button',{name:'查看钱包',exact:true}).click();await ledger();await check(['me','wallet','ledger'],'320px 200% from wallet');
  return {passed:results.length,results,orderDateRule:'今天 09:00 / 08-28 unchanged',detailTimestamp:'2026-09-30 14:00 unchanged'};
}
