(() => {
'use strict';
const $ = id => document.getElementById(id);
let result = null, revision = 0, imageURL = null, noticeTimer, registration, updateRequested = false, installPrompt;
const standalone = () => window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

function notice(text) {
  $('notice').textContent = text; $('notice').hidden = false;
  clearTimeout(noticeTimer); noticeTimer = setTimeout(() => $('notice').hidden = true, 6000);
}
function invalidate() {
  revision++; result = null;
  for (const id of ['share-png','download-png','download-svg']) $(id).disabled = true;
  if (imageURL) { URL.revokeObjectURL(imageURL); imageURL = null; }
  $('qr-image').hidden = true; $('qr-image').removeAttribute('src'); $('placeholder').hidden = false;
  $('destination').hidden = true; $('encoded-url').textContent = '';
  $('result-tag').textContent = $('url').value.trim() ? '作成待ち' : '入力待ち'; $('result-tag').classList.remove('ready');
  $('error').hidden = true; $('url').removeAttribute('aria-invalid'); $('dimensions').textContent = '白背景・黒のコード';
}
function normalize(raw) {
  const text = raw.trim();
  if (!text) throw new Error('URLを入力してください．');
  if (text.length > 12000) throw new Error('URLが長すぎます．');
  if (/[\x00-\x20\x7f\\]/u.test(text)) throw new Error('URLの途中に空白・改行・「\\」が含まれています．URLをコピーし直してください．');
  if (/%(?![\da-f]{2})/i.test(text)) throw new Error('URLの「%」以降の表記を確認してください．');
  let candidate = text;
  if (!/^https?:\/\//i.test(text)) {
    if (/^[a-z][a-z\d+.-]*:/i.test(text) && !/^[^/?#]+:\d+(?:[/?#]|$)/.test(text)) throw new Error('http または https のURLを入力してください．');
    candidate = 'https://' + text;
  }
  let url;
  try { url = new URL(candidate); } catch (_) { throw new Error('URLの形式を確認してください．例：https://example.com'); }
  if (!['http:','https:'].includes(url.protocol) || !url.hostname) throw new Error('WebページのURLを入力してください．');
  if (url.username || url.password) throw new Error('ユーザー名・パスワードを含まないURLを入力してください．');
  if (!url.hostname.includes('.') && url.hostname !== 'localhost' && !url.hostname.startsWith('[')) throw new Error('ドメイン名を確認してください．例：example.com');
  if (!/^[\x21-\x7e]+$/.test(url.href)) throw new Error('URLを変換できませんでした．ブラウザーのアドレス欄からコピーしてください．');
  return url.href;
}
function pngBlob(canvas) {
  return new Promise((resolve,reject) => canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('画像を作成できませんでした．画像サイズを小さくしてください．')), 'image/png'));
}
async function generate() {
  invalidate(); const token = revision;
  $('generate').disabled = true; $('generate').textContent = '作成中…';
  try {
    const url = normalize($('url').value), pixels = Number($('size').value), ecc = $('ecc').value;
    await new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 0)));
    let qr;
    try { qr = qrcodegen.QrCode.encodeSegments(qrcodegen.QrSegment.makeSegments(url), qrcodegen.QrCode.Ecc[ecc], 1, 40, -1, false); }
    catch (error) { if (error instanceof RangeError) throw new Error('URLが長すぎます．短くするか，誤り訂正をLにしてください．'); throw error; }
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = pixels;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('画像を作成できませんでした．');
    ctx.imageSmoothingEnabled = false; ctx.fillStyle = '#fff'; ctx.fillRect(0,0,pixels,pixels);
    const scale = Math.floor(pixels/(qr.size+8)), offset = Math.floor((pixels-qr.size*scale)/2);
    ctx.fillStyle = '#000'; const path = [];
    for (let y=0;y<qr.size;y++) for (let x=0;x<qr.size;x++) if (qr.getModule(x,y)) {
      ctx.fillRect(offset+x*scale,offset+y*scale,scale,scale); path.push(`M${x+4} ${y+4}h1v1h-1z`);
    }
    const png = await pngBlob(canvas); canvas.width = canvas.height = 1;
    if (token !== revision) return;
    const svgText = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${pixels}" height="${pixels}" viewBox="0 0 ${qr.size+8} ${qr.size+8}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="white"/><path fill="black" d="${path.join('')}"/></svg>\n`;
    result = {url,pixels,png,svg:new Blob([svgText],{type:'image/svg+xml'})};
    imageURL = URL.createObjectURL(png); $('qr-image').src = imageURL;
    $('qr-image').width = $('qr-image').height = pixels;
    $('qr-image').hidden = false; $('placeholder').hidden = true; $('destination').hidden = false;
    $('encoded-url').textContent = url; $('result-tag').textContent = '作成済み'; $('result-tag').classList.add('ready');
    $('dimensions').textContent = `${pixels} × ${pixels} px`;
    for (const id of ['share-png','download-png','download-svg']) $(id).disabled = false;
    $('url').blur();
  } catch (error) {
    if (token === revision) { $('error').textContent = error.message || 'QRコードを作成できませんでした．'; $('error').hidden = false; $('url').setAttribute('aria-invalid','true'); }
  } finally {
    $('generate').disabled = false; $('generate').innerHTML = 'QRコードを作る <span aria-hidden="true">→</span>';
  }
}
function download(blob, extension) {
  const href = URL.createObjectURL(blob), anchor = document.createElement('a');
  anchor.href = href; anchor.download = `KimagureQR.${extension}`; document.body.appendChild(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(href), 60000);
  notice('保存先を選んでください．端末によってはダウンロード欄に保存されます．');
}
async function sharePNG() {
  if (!result) return;
  const file = new File([result.png], 'KimagureQR.png', {type:'image/png'});
  if (navigator.canShare?.({files:[file]}) && navigator.share) {
    try { await navigator.share({files:[file]}); }
    catch (error) { if (error.name !== 'AbortError') notice('共有できませんでした．画像の長押しか「PNGを保存」をお試しください．'); }
  } else {
    $('qr-image').scrollIntoView({behavior:'smooth',block:'center'});
    notice('QR画像を長押しして保存するか，「PNGを保存」を押してください．');
  }
}
function offlineState(kind,text) {
  $('offline-status').className = 'offline-status ' + kind; $('offline-text').textContent = text;
  $('retry-offline').hidden = kind !== 'failed';
}
function checkCache(worker) {
  return new Promise((resolve,reject) => {
    const channel = new MessageChannel();
    const timeout = setTimeout(() => {channel.port1.close();reject(new Error('timeout'));},6000);
    channel.port1.onmessage = event => {clearTimeout(timeout);channel.port1.close();resolve(event.data);};
    worker.postMessage({type:'CHECK_OFFLINE'},[channel.port2]);
  });
}
async function confirmOffline() {
  try {
    const worker = navigator.serviceWorker.controller;
    if (!worker) return;
    const status = await checkCache(worker);
    if (!status.ready) throw new Error('missing cache');
    offlineState('ready','オフライン利用の準備完了');
    if (standalone() && navigator.storage?.persist) navigator.storage.persist().catch(() => {});
  } catch (_) { offlineState('failed','オフライン用データを確認できません．ネット接続中に準備し直してください．'); }
}
async function setupOffline() {
  if (!('serviceWorker' in navigator) || !window.isSecureContext) {
    offlineState('failed','この画面ではオフライン登録ができません．SafariまたはChromeで開いてください．'); return;
  }
  offlineState('','オフライン利用を準備中…');
  try {
    registration = await navigator.serviceWorker.register('./sw.js',{updateViaCache:'none'});
    const watch = () => { $('update-button').hidden = !registration.waiting; };
    watch(); registration.addEventListener('updatefound',() => {
      const installing = registration.installing;
      installing?.addEventListener('statechange',() => {
        if (installing.state === 'installed') {watch(); confirmOffline();}
        if (installing.state === 'redundant') offlineState('failed','準備を完了できませんでした．ネット接続中にやり直してください．');
      });
    });
    // Limit waiting if installation fails; never show ready based only on navigator.onLine.
    await Promise.race([navigator.serviceWorker.ready,new Promise((_,reject)=>setTimeout(()=>reject(new Error('timeout')),20000))]);
    if (navigator.serviceWorker.controller) await confirmOffline();
  } catch (_) {
    if (navigator.serviceWorker.controller) await confirmOffline();
    else offlineState('failed','オフラインの準備ができていません．ネット接続中にやり直してください．');
  }
}
$('qr-form').addEventListener('submit',event=>{event.preventDefault();generate();});
$('url').addEventListener('input',invalidate);
for (const id of ['size','ecc']) $(id).addEventListener('change',invalidate);
$('clear').addEventListener('click',()=>{$('url').value='';invalidate();$('url').focus();});
$('share-png').addEventListener('click',sharePNG);
$('download-png').addEventListener('click',()=>{if(result)download(result.png,'png');});
$('download-svg').addEventListener('click',()=>{if(result)download(result.svg,'svg');});
$('retry-offline').addEventListener('click',async()=>{
  // Normal navigation lets the active worker refill any missing application files.
  offlineState('','オフライン用データを再確認中…');
  try { await Promise.all(['index.html','app.css','app.js','qrcodegen.js','manifest.webmanifest','icon.svg','icon-180.png','icon-192.png','icon-512.png','LICENSE.txt'].map(path=>fetch(path,{cache:'reload'}).then(r=>{if(!r.ok)throw new Error('fetch');}))); await setupOffline(); }
  catch (_) {offlineState('failed','準備できませんでした．ネット接続と空き容量を確認してください．');}
});
$('update-button').addEventListener('click',()=>{
  if (!registration?.waiting) return;
  if ($('url').value.trim() && !window.confirm('更新すると入力内容とQRコードが消えます．更新しますか？')) return;
  updateRequested = true; registration.waiting.postMessage({type:'SKIP_WAITING'});
});
if ('serviceWorker' in navigator) navigator.serviceWorker.addEventListener('controllerchange',()=>{if(updateRequested)location.reload();else confirmOffline();});
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();installPrompt=event;$('install-button').hidden=false;});
$('install-button').addEventListener('click',async()=>{if(installPrompt){await installPrompt.prompt();installPrompt=null;$('install-button').hidden=true;}});
window.addEventListener('appinstalled',()=>{$('install-guide').open=false;});
window.addEventListener('pageshow',()=>{if(navigator.serviceWorker?.controller)confirmOffline();});
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&navigator.serviceWorker?.controller)confirmOffline();});
$('install-guide').open = !standalone();
setupOffline();
})();
