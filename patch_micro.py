from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function abrirModalMicro(tid){ microAlvo=tid; const t=tarefas.find(t=>t.id===tid); document.getElementById('microTitulo').textContent='Nova micro ação — '+(t?t.atividade.substring(0,45)+(t.atividade.length>45?'…':''):''); document.getElementById('ovMicro').classList.add('open'); expandedTarefa[tid]=true; }
function fecharModalMicro(){ document.getElementById('ovMicro').classList.remove('open'); ['mDesc','mResp','mPrazo'].forEach(id=>document.getElementById(id).value=''); document.getElementById('mStatus').value=''; document.getElementById('mPrio').value=''; document.getElementById('errMicro').style.display='none'; microAlvo=null; }
async function salvarMicro(){
  const desc=document.getElementById('mDesc').value.trim();
  if(!desc){document.getElementById('errMicro').style.display='block';document.getElementById('mDesc').focus();return;}
  document.getElementById('errMicro').style.display='none';
  const t=tarefas.find(t=>t.id===microAlvo);
  if(t){ t.micros.push({id:nextMicroId++,desc,responsavel:document.getElementById('mResp').value.trim(),prazo:document.getElementById('mPrazo').value,status:document.getElementById('mStatus').value,prio:document.getElementById('mPrio').value}); }
  try { await salvarDados(); } catch(e) { alert('Não foi possível salvar a micro ação no banco. Verifique sua conexão e tente novamente.'); console.error(e); return; }
  fecharModalMicro(); render();
}
"""
new="""let microEditando = null;
function abrirModalMicro(tid, mid=null){
  microAlvo=tid; microEditando=mid!==null ? Number(mid) : null;
  const t=tarefas.find(t=>t.id===tid);
  const m=microEditando!==null && t ? t.micros.find(x=>Number(x.id)===microEditando) : null;
  document.getElementById('microTitulo').textContent=(m?'Editar micro ação':'Nova micro ação')+' — '+(t?t.atividade.substring(0,45)+(t.atividade.length>45?'…':''):'');
  document.getElementById('mDesc').value=m?.desc||'';
  document.getElementById('mResp').value=m?.responsavel||'';
  document.getElementById('mPrazo').value=m?.prazo||'';
  document.getElementById('mStatus').value=m?.status||'';
  document.getElementById('mPrio').value=m?.prio||'';
  document.getElementById('errMicro').style.display='none';
  document.getElementById('ovMicro').classList.add('open'); expandedTarefa[tid]=true;
}
function fecharModalMicro(){ document.getElementById('ovMicro').classList.remove('open'); ['mDesc','mResp','mPrazo'].forEach(id=>document.getElementById(id).value=''); document.getElementById('mStatus').value=''; document.getElementById('mPrio').value=''; document.getElementById('errMicro').style.display='none'; microAlvo=null; microEditando=null; }
async function salvarMicro(){
  const desc=document.getElementById('mDesc').value.trim();
  if(!desc){document.getElementById('errMicro').style.display='block';document.getElementById('mDesc').focus();return;}
  document.getElementById('errMicro').style.display='none';
  const t=tarefas.find(t=>t.id===microAlvo); if(!t) return;
  const dados={desc,responsavel:document.getElementById('mResp').value.trim(),prazo:document.getElementById('mPrazo').value,status:document.getElementById('mStatus').value,prio:document.getElementById('mPrio').value};
  if(microEditando!==null){ const m=t.micros.find(x=>Number(x.id)===microEditando); if(m) Object.assign(m,dados); }
  else t.micros.push({id:nextMicroId++,...dados});
  try { await salvarDados(); } catch(e) { alert('Não foi possível salvar a micro ação no banco. Verifique sua conexão e tente novamente.'); console.error(e); return; }
  fecharModalMicro(); render();
}
"""
if old not in s: raise SystemExit('micro block not found')
s=s.replace(old,new,1)
old_row="""<td style=\"display:flex;align-items:center;justify-content:space-between\">${prioLabel(m.prio)}<button class=\"btn-icon\" style=\"font-size:13px\" onclick=\"excluirMicro(${t.id},${m.id})\" title=\"Excluir micro ação\"><i class=\"ti ti-x\"></i></button></td>"""
new_row="""<td style=\"display:flex;align-items:center;justify-content:space-between\">${prioLabel(m.prio)}<span style=\"display:inline-flex;gap:2px\"><button class=\"btn-icon\" style=\"font-size:13px\" onclick=\"abrirModalMicro(${t.id},${m.id})\" title=\"Editar micro ação\"><i class=\"ti ti-pencil\"></i></button><button class=\"btn-icon\" style=\"font-size:13px\" onclick=\"excluirMicro(${t.id},${m.id})\" title=\"Excluir micro ação\"><i class=\"ti ti-trash\"></i></button></span></td>"""
if old_row not in s: raise SystemExit('micro row not found')
s=s.replace(old_row,new_row,1)
old_del="""async function excluirMicro(tid,mid){ const t=tarefas.find(t=>t.id===tid); if(t){ t.micros=t.micros.filter(m=>m.id!==mid); salvarDados(); if(sb) await sb.from('micro_acoes').delete().eq('id',String(mid)); render(); } }"""
new_del="""async function excluirMicro(tid,mid){
  const t=tarefas.find(t=>t.id===tid); if(!t) return;
  if(!confirm('Excluir esta micro ação?')) return;
  const antiga=t.micros.slice();
  try {
    if(sb){ const {error}=await sb.from('micro_acoes').delete().eq('id',String(mid)); if(error) throw error; }
    t.micros=t.micros.filter(m=>Number(m.id)!==Number(mid));
    localStorage.setItem('tarefas',JSON.stringify(tarefas)); render();
  } catch(e) { t.micros=antiga; alert('Não foi possível excluir a micro ação do banco.\\n\\nErro: '+(e.message||'erro desconhecido')); }
}"""
if old_del not in s: raise SystemExit('delete function not found')
s=s.replace(old_del,new_del,1)

old_toolbar="""  <div class="toolbar">
    <input type="text" id="busca" placeholder="Buscar por atividade ou responsável…" oninput="render()">
    <button class="btn-primary" onclick="abrirModalTarefa()"><i class="ti ti-plus"></i> Nova tarefa</button>
  </div>"""
new_toolbar="""  <div class="toolbar">
    <input type="text" id="busca" placeholder="Buscar por atividade ou responsável…" oninput="render()">
    <select id="filtroStatus" onchange="render()" title="Filtrar por status" style="height:36px;padding:0 10px;border:0.5px solid #c8c8c4;border-radius:8px;background:#fff;color:#1a1a18;font-size:14px;font-family:inherit;outline:none;min-width:170px;cursor:pointer">
      <option value="">Todos os status</option>
      <option value="Pendente">Pendente</option>
      <option value="Aguardando">Aguardando</option>
      <option value="Concluído">Concluído</option>
      <option value="__sem_status__">Sem status</option>
    </select>
    <button class="btn-primary" onclick="abrirModalTarefa()"><i class="ti ti-plus"></i> Nova tarefa</button>
  </div>"""
if old_toolbar not in s: raise SystemExit('toolbar patch source not found')
s=s.replace(old_toolbar,new_toolbar,1)

old_render="""function render() {
  const busca = document.getElementById('busca').value.toLowerCase();
  let lista = tarefas;
  if (busca) lista = lista.filter(t => t.atividade.toLowerCase().includes(busca) || t.solicitante.toLowerCase().includes(busca) || t.responsavel.toLowerCase().includes(busca) || t.micros.some(m => m.desc.toLowerCase().includes(busca) || m.responsavel.toLowerCase().includes(busca)));"""
new_render="""function render() {
  const busca = document.getElementById('busca').value.toLowerCase();
  const filtroStatus = document.getElementById('filtroStatus')?.value || '';
  let lista = tarefas;
  if (busca) lista = lista.filter(t => t.atividade.toLowerCase().includes(busca) || t.solicitante.toLowerCase().includes(busca) || t.responsavel.toLowerCase().includes(busca) || t.micros.some(m => m.desc.toLowerCase().includes(busca) || m.responsavel.toLowerCase().includes(busca)));
  if (filtroStatus) lista = lista.filter(t => filtroStatus === '__sem_status__' ? !t.status : t.status === filtroStatus);"""
if old_render not in s: raise SystemExit('render patch source not found')
s=s.replace(old_render,new_render,1)

p.write_text(s,encoding='utf-8')
