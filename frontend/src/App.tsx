import { useEffect, useMemo, useState } from 'react'
import type { Artifact, AgentRun } from './types'
import { api } from './api'
import Artifact3D from './Artifact3D'
import ExperienceWorld from './ExperienceWorld'

type Tab = 'experience' | 'story' | 'timeline' | 'facts'

const experienceNames: Record<string, string> = {
  human_timeline: 'مختبر الهجرة القديمة', residue_lab: 'مختبر البقايا', paleo_climate: 'مختبر المناخ القديم', deep_time: 'بوابة الزمن العميق',
  trace_engraving: 'ورشة تتبع النقش', meteorite_path: 'محاكاة دخول النيزك', pattern_studio: 'استوديو الزخرفة', edge_lab: 'مختبر الضوء والسطح',
  arrow_builder: 'ورشة تركيب الأداة', smelting_air: 'فرن الصهر', trade_scale: 'مختبر التوازن', medical_zoom: 'مختبر فحص الأداة', calligraphy_zoom: 'استوديو الخط',
  cube_story: 'غرفة الوجوه الأربعة', craft_detail: 'طاولة الصانع', lamp_heat: 'مختبر الضوء والحرارة', ink_write: 'المحبرة والورق', silver_craft: 'مختبر المعدن واللمعة',
  architecture_rebuild: 'ورشة بناء العمود', pilgrimage_route: 'رحلة على درب زبيدة', lock_ring: 'مختبر الحلقة والقفل', foundation_stone: 'ورشة حجر الأساس',
  gold_ornament: 'ورشة الصائغ', bronze_frieze: 'ورشة النقش البرونزي', wall_tile: 'استوديو بناء الجدار'
}

function speak(text: string) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ar-SA'
  u.rate = .88
  window.speechSynthesis.speak(u)
}

function App() {
  const [items, setItems] = useState<Artifact[]>([])
  const [selected, setSelected] = useState<Artifact | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    api.artifacts().then(setItems).catch(() => setError('تعذر الاتصال بالخادم. شغّل Backend على المنفذ 8000 ثم أعد تحميل الصفحة.')).finally(() => setLoading(false))
  }, [])
  if (selected) return <Experience artifact={selected} onBack={() => setSelected(null)} />
  return <Gallery items={items} loading={loading} error={error} onSelect={setSelected} />
}

function Gallery({ items, loading, error, onSelect }: { items: Artifact[]; loading: boolean; error: string; onSelect: (a: Artifact) => void }) {
  return <main className="page" dir="rtl">
    <header className="topbar">
      <div className="brand"><div className="logo">رُ</div><div><b>رُوي</b><span>تجربة التراث التفاعلية</span></div></div>
      <div className="status"><i /> {items.length} قطعة · تجربة 3D مستقلة · Agentic AI</div>
    </header>
    <section className="hero">
      <div>
        <span className="eyebrow">المتحف · الذاكرة · التفاعل</span>
        <h1>التاريخ<br /><em>يُرى ويُلمس.</em></h1>
        <p>كل قطعة لها عالمان: مجسمها ثلاثي الأبعاد للفحص، وتجربة 3D مستقلة يدخلها الزائر بيده. الحكاية والخط الزمني والحقائق والصوت والـAgent جزء من الرحلة.</p>
        <div className="heroActions"><span>👆 لمس مباشر</span><span>🔊 سرد عربي</span><span>✦ Agentic Experience</span></div>
      </div>
      <div className="heroNumbers"><div><b>{items.length || 25}</b><span>قطعة</span></div><div><b>{items.length}</b><span>تجربة 3D</span></div><div><b>360°</b><span>فحص</span></div></div>
    </section>
    {loading && <div className="loadingCard">جاري تحميل مجموعة القطع…</div>}
    {error && <div className="errorCard">{error}</div>}
    <section className="grid">
      {items.filter(a => a.id <= 20).map((a) => <button key={a.id} className="card" onClick={() => onSelect(a)}>
        <div className="thumb"><img src={a.image} alt={a.name_ar} loading="lazy" /><span className="num">{String(a.id).padStart(2, '0')}</span><span className="exp">{experienceNames[a.experience_type] || a.experience}</span></div>
        <div className="ct"><small>{a.age} · {a.location}</small><h2>{a.name_ar}</h2><p>{a.material}</p><b>ادخل التجربة ←</b></div>
      </button>)}
    </section>
  </main>
}

function Experience({ artifact, onBack }: { artifact: Artifact; onBack: () => void }) {
  const [tab, setTab] = useState<Tab>('experience')
  const [agent, setAgent] = useState<AgentRun | null>(null)
  const [progress, setProgress] = useState(.08)
  const [modelReady, setModelReady] = useState(false)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [asking, setAsking] = useState(false)

  useEffect(() => { api.agents(artifact.id).then(setAgent).catch(() => setAgent(null)) }, [artifact.id])
  const intro = useMemo(() => `${artifact.story} ${artifact.description_ar}`, [artifact])
  const ask = async () => {
    if (!question.trim()) return
    setAsking(true)
    try { const r = await api.chat(artifact.id, question.trim()); setAnswer(r.answer) } catch { setAnswer('تعذر الوصول إلى الوكيل الآن. جرّب السؤال مرة أخرى.') } finally { setAsking(false) }
  }

  return <main className="experiencePage" dir="rtl">
    <header className="topbar sticky">
      <button className="backButton" onClick={onBack}>← العودة للمجموعة</button>
      <div className="brand"><div className="logo">رُ</div><div><b>رُوي</b><span>مختبر القطعة</span></div></div>
      <button className="soundButton" onClick={() => speak(intro)}>🔊 اسمع الحكاية</button>
    </header>

    <div className="experienceLayout">
      <section className="artifactPanel">
        <div className="panelLabel"><span>ARTIFACT 3D</span><b>{modelReady ? 'جاهز للفحص' : 'جاري تحميل المجسم…'}</b></div>
        <div className="artifactViewer"><Artifact3D artifact={artifact} onLoaded={setModelReady} /></div>
        <div className="viewerHint">👆 افحص القطعة مباشرة · قرّب بإصبعين · اسحب لتدويرها · التجربة التفاعلية مستقلة عن المجسم</div>
        <div className="artifactMeta"><span>{artifact.material}</span><span>{artifact.age}</span><span>{artifact.location}</span></div>
      </section>

      <section className="infoPanel">
        <span className="eyebrow">{artifact.name_en} · {artifact.location}</span>
        <h1>{artifact.name_ar}</h1>
        <p className="lead">{artifact.description_ar}</p>
        <div className="tabs">{([['experience','التجربة'],['story','حكاية القطعة'],['timeline','الخط الزمني'],['facts','حقائق سريعة']] as [Tab,string][]).map(([id,label]) => <button className={tab===id?'active':''} key={id} onClick={() => setTab(id)}>{label}</button>)}</div>
        {tab === 'experience' && <>
          <div className="agentCard"><div className="agentTop"><span>✦ Agent-designed</span><b>{experienceNames[artifact.experience_type] || artifact.experience}</b></div><p>{agent?.experience_plan || artifact.prompt}</p><div className="agentPills"><span>Touch-first</span><span>3D World</span><span>Audio</span><span>Adaptive Hint</span><span>Scene-driven</span></div>{agent?.experience_script_ar&&<div className="experienceScript"><b>سيناريو التجربة</b><p>{agent.experience_script_ar}</p></div>}</div>
          <div className="worldPanel"><ExperienceWorld artifact={artifact} onProgress={setProgress} /></div>
          <div className="progressStrip"><span>استجابة التجربة</span><b>{Math.round(progress*100)}%</b><i><em style={{ width: `${Math.round(progress*100)}%` }} /></i></div>
        </>}
        {tab === 'story' && <InfoCard title="حكاية القطعة" text={artifact.story} onSpeak={() => speak(artifact.story)} />}
        {tab === 'timeline' && <div className="timeline">{artifact.timeline.map(([date,text]) => <div className="timelineItem" key={date}><b>{date}</b><p>{text}</p></div>)}</div>}
        {tab === 'facts' && <div className="facts">{artifact.facts.map((f) => <div key={f}>✦ {f}</div>)}</div>}

        <div className="askCard"><div><span>Ruwi Agent</span><b>اسأل عن القطعة</b></div><div className="askRow"><input value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')void ask()}} placeholder="مثلاً: ما الذي يجعل هذه القطعة مهمة؟" /><button onClick={() => void ask()} disabled={asking}>{asking?'…':'اسأل'}</button></div>{answer&&<p className="answer">{answer}</p>}</div>
      </section>
    </div>
  </main>
}

function InfoCard({ title, text, onSpeak }: { title: string; text: string; onSpeak: () => void }) {
  return <div className="infoCard"><div className="infoCardHead"><h2>{title}</h2><button onClick={onSpeak}>🔊 استمع</button></div><p>{text}</p></div>
}

export default App
