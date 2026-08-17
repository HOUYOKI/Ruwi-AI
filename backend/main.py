from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'artifacts.json'
ARTIFACTS=json.loads(DATA.read_text(encoding='utf-8'))
BY_ID={int(a['id']):a for a in ARTIFACTS}
app=FastAPI(title='Ruwi Touch Exhibition API',version='8.0.0')
origins=os.getenv('FRONTEND_ORIGIN','http://127.0.0.1:5173').split(',')
app.add_middleware(CORSMiddleware,allow_origins=origins+['http://localhost:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.mount('/artifacts-media',StaticFiles(directory=str(ROOT.parent/'frontend'/'public')),name='media')

@app.get('/health')
def health(): return {'ok':True,'artifacts':len(ARTIFACTS),'agents':['curator','historian','experience_designer','narrator']}

@app.get('/artifacts')
def artifacts(): return ARTIFACTS

@app.get('/artifacts/{artifact_id}')
def artifact(artifact_id:int):
    a=BY_ID.get(artifact_id)
    if not a: raise HTTPException(404,'Artifact not found')
    return a

def curator(a:dict[str,Any])->str:
    return f"القطعة {a['name_ar']} تُقدَّم من خلال بياناتها الأساسية: {a['material']}، {a['age']}، وموقعها {a['location']}."
def historian(a:dict[str,Any])->str:
    return a['description_ar']
EXPERIENCE_AGENT_PLANS={
    'human_timeline': 'يبني مشهدًا زمنيًا من أربع طبقات؛ يتقدم الزائر بالسحب ثم يفتح طبقات الإنسان والبيئة والسياق.',
    'residue_lab': 'يحوّل القطعة إلى مختبر تنقيب: كشف طبقات، نقاط فحص، ثم استنتاج بصري من البقايا.',
    'paleo_climate': 'يصمم انتقالًا مناخيًا تدريجيًا تتغير معه الإضاءة والجسيمات والمشهد بدل تبديل شاشة ثابتة.',
    'deep_time': 'يستخدم حلقات ومقياسًا بصريًا لتمثيل اتساع الزمن بدل الاكتفاء بأرقام على خط زمني.',
    'trace_engraving': 'يحوّل النقش إلى مسار فحص ضوئي مع تتبع بإصبع الزائر.',
    'meteorite_path': 'يبني مسارًا تفاعليًا من الفضاء إلى الغلاف الجوي والسقوط والوصول مع محاكاة صوتية.',
    'pattern_studio': 'يحوّل الزخرفة إلى نظام تكرار وتماثل يمكن للزائر تغييره ثم فحصه على النموذج.',
    'edge_lab': 'يستخدم مصدر ضوء تفاعلي وزوايا فحص لإظهار تفاصيل سطح السبج.',
    'arrow_builder': 'يبني تركيبًا بصريًا للأجزاء والزاوية دون تقديم إرشادات استخدام سلاح.',
    'smelting_air': 'يحوّل الصهر إلى حلقة نفخ-حرارة-توهج؛ كل ضغطة تزيد تدفق الهواء وتغير المشهد.',
    'trade_scale': 'يستخدم أوزانًا افتراضية وحركة عارضة حقيقية للوصول إلى التوازن.',
    'medical_zoom': 'يبني عدسة فحص تنقل الزائر بين مناطق القطعة بدل التكبير السلبي.',
    'calligraphy_zoom': 'يحوّل الخط إلى مسار يمكن تتبعه بالإصبع مع صوت قلم محاكى.',
    'cube_story': 'يجعل كل وجه من أوجه المذبح فصلًا لا يفتح إلا بعد اكتشافه.',
    'craft_detail': 'يقسم الحرفة إلى مواد ومراحل فحص مع إضاءة وصوت مختلفين لكل مادة.',
    'lamp_heat': 'يبني دورة لهب وضوء تدريجية بحيث يرى الزائر أثر الحرارة على المشهد.',
    'ink_write': 'يجعل المحبرة أداة كتابة فعلية على شاشة اللمس مع مراحل غمس وضغط وأثر.',
    'silver_craft': 'يحوّل الزخرفة إلى مهمة جمع لمعات وفحص للمقبض والغمد.',
    'architecture_rebuild': 'يبني العمود طبقة بعد طبقة حتى يظهر السياق المعماري.',
    'pilgrimage_route': 'يحوّل المسار إلى رحلة قابلة للسحب مع محطات توقف وطبقات سردية.',
    'lock_ring': 'يبني محاذاة دورانية للحلقة مع نقاط نقش وتثبيت، ثم يفتح فحصًا جانبيًا للمعدن.',
    'foundation_stone': 'يحوّل حجر الأساس إلى ورشة بناء: طبقات ترتفع تدريجيًا ويتغير موضع القطعة وإضاءتها مع التقدم.',
    'gold_ornament': 'يصمم مهمة صائغ: تثبيت ستة أحجار حول المركز ثم اختبار انعكاس الذهب بالدوران والضوء.',
    'bronze_frieze': 'يحوّل الشريط البرونزي إلى ورشة نقش لمسّية مع تتبع السطر وتغيير زاوية الإضاءة.',
    'wall_tile': 'يبني تركيبًا معماريًا من أربع وحدات زخرفية حول البلاطة ويكشف التماثل تدريجيًا.'
}


EXPERIENCE_SCRIPTS={
1:'تبدأ الرحلة في موقع تنقيب طبقي. يمسك الزائر فرشاة صغيرة ويزيل الغبار تدريجيًا، ثم تظهر الطبقة الأقدم والأثر المدفون. لا توجد مراحل منفصلة؛ حركة اليد نفسها هي التي تكشف المشهد وتغيّر الإضاءة والصوت.',
2:'يتحول الوعاء إلى مختبر آثار مصغر. يحرك الزائر أداة الفحص داخل الوعاء، فتتحرك البقايا والسائل وتظهر مؤشرات على المواد المكتشفة. الهدف هو ملاحظة التفاصيل قبل قراءة التفسير.',
3:'يدخل الزائر إلى بيئة الجزيرة القديمة. تحريك السحب يغيّر المطر والماء والنباتات، بينما يبقى الحيوان المتحجر مرجعًا بصريًا ثابتًا. المشهد يشرح اختلاف البيئة من خلال التحول المرئي لا من خلال شاشة مراحل.',
4:'يصبح الجذع سجلًا مناخيًا بصريًا. يحرك الزائر الماسح عبر الخشب، فتظهر حلقات النمو واحدة بعد أخرى ويتبدل الضوء على سطحها. كل حركة تقربه من قراءة الشجرة كوثيقة زمنية.',
5:'في كهف مظلم، لا يظهر النقش مباشرة. يحرك الزائر المشعل بزاوية منخفضة فوق الجدار، فتظهر آثار السطح والفراغات تدريجيًا. الصوت والظل والضوء يتغيرون مع موضع اليد.',
6:'يبدأ النيزك من السماء وينتهي عند سطح الأرض. الزائر يسحبه بنفسه خلال المسار، وكلما اقترب من الغلاف الجوي يزداد التوهج والدخان والسرعة حتى يصل إلى لحظة الاصطدام.',
7:'تتحول الورشة إلى عجلة فخار. يمسك الزائر كتلة الطين ويحرك يده حولها، فتتغير نسب الجسم وارتفاعه وحافته بينما تدور العجلة. النتيجة شكل ثلاثي الأبعاد يتكون من حركة الزائر.',
8:'في ورشة الحجر، يضع الزائر المطرقة فوق حافة الأداة ويضربها بحركة يده. تظهر شظايا وغبار ويتغير شكل الحافة تدريجيًا، فيشاهد أثر الصنعة بدل مشاهدة Animation جاهز.',
9:'تُعرض مكونات الأداة على طاولة صانع. يسحب الزائر الرأس والريشة والرباط إلى مواضعها، وتستجيب القطع عندما تقترب من المحاذاة الصحيحة حتى يكتمل الشكل.',
10:'تبدأ الورشة بفرن خامد. يحرك الزائر المنفاخ لزيادة الهواء، فتتغير النار وتوهج المعدن. بعدها يرفع البوتقة ويقربها من القالب ليشاهد انتقال المادة من حالة ساخنة إلى عملية صب متخيلة داخل المشهد.',
11:'في سوق قديم، يضع الزائر الأوزان على الكفتين. العارضة تميل فعليًا مع كل وزن، والهدف هو إيجاد التوازن لا الوصول إلى رقم في شريط. عند الاتزان يتغير الضوء وتظهر رسالة إتمام الصفقة.',
12:'تتحول القطعة إلى محطة فحص. يبدأ الزائر بتنظيف السطح، ثم يحرك العدسة فوق المناطق الدقيقة. الإضاءة والانعكاس يكشفان تفاصيل صغيرة تدريجيًا، وكأن الزائر يعمل في مختبر حفظ.',
13:'الكتابة لا تظهر كاملة في البداية. يحرك الزائر مصباحًا جانبيًا، فتتغير الظلال وتبرز الحروف المحفورة. بعد ظهورها يمكن تتبع الخط بإصبعه ومشاهدة القراءة تتقدم.',
14:'تُعرض عناصر المشهد حول مذبح حجري. ينقلها الزائر بيده ويعيد ترتيبها في البيئة، وعندما يقترب التكوين من الوضع المقصود يستجيب المشهد بالضوء والظل بدل الانتقال إلى شاشة جديدة.',
15:'يظهر نموذج آلية ميكانيكية مكشوف. يدور الزائر الحلقة ببطء حتى تصطف الأسنان، ثم يسحب المزلاج. الهدف هو فهم الحركة الداخلية من خلال لمس الأجزاء نفسها.',
16:'تبدأ الغرفة مظلمة. يسحب الزائر الزيت إلى الخزان ثم يرفع الفتيل، فيتغير حجم اللهب وينتشر الضوء على الجدران والأرضية. النتيجة هي تحول بصري كامل للبيئة.',
17:'يجلس الزائر أمام مكتب الكتابة. يلمس المحبرة ثم يحرك القلم فوق الورق، فيترك أثرًا بصريًا متتابعًا. كلما تحرك القلم تغيرت كثافة العلامات حتى تتكون صفحة كاملة.',
18:'يبدأ المشهد بالغمد مغلقًا. يسحبه الزائر ليكشف النصل، ثم يحرك مصدر ضوء الفحص على المعدن. الانعكاسات تتغير لحظيًا لتبرز الزخرفة والسطح بدل استخدام صورة ثابتة.',
19:'في ورشة البناء، تنتظر كتل الحجر على الأرض. يسحب الزائر كل كتلة إلى مكانها، وعندما تستقر تظهر طبقة جديدة. في النهاية يرفع التاج فوق العمود ويكتمل المشهد المعماري.',
20:'تبدأ الرحلة على خريطة ثلاثية الأبعاد للطريق. يسحب الزائر المسافر بين المحطات، وتظهر عناصر الماء والظل والاستراحة على طول المسار. التقدم هنا رحلة مستمرة وليست قائمة مراحل.'
}

def experience_designer(a:dict[str,Any])->str:
    plan=EXPERIENCE_AGENT_PLANS.get(a['experience_type'], a['prompt'])
    return f"وكيل التجربة اختار نمط {a['experience_type']} لهذه القطعة لأن طبيعتها تسمح بتفاعل ملموس. الخطة: {plan}"
def narrator(a:dict[str,Any])->str:
    return a['story']

def run_agents(a):
    return {'curator':curator(a),'historian':historian(a),'experience_designer':experience_designer(a),'narrator':narrator(a),'recommended':a['experience_type'],'experience_plan':EXPERIENCE_AGENT_PLANS.get(a['experience_type'],a['prompt']),'experience_script_ar':EXPERIENCE_SCRIPTS.get(a['id'],a['prompt'])}

@app.get('/agents/{artifact_id}')
def agents(artifact_id:int):
    a=BY_ID.get(artifact_id)
    if not a: raise HTTPException(404,'Artifact not found')
    return run_agents(a)

class ChatRequest(BaseModel): artifact_id:int; question:str

async def llm_answer(a:dict[str,Any],q:str)->str|None:
    key=os.getenv('ANTHROPIC_API_KEY','').strip()
    if not key:return None
    model=os.getenv('CLAUDE_MODEL','claude-sonnet-4-5')
    system=('أنت رُوي، وكيل تفسير أثري في معرض تفاعلي. أجب بالعربية فقط. '
            'التزم بالمعلومات الموجودة في بطاقة القطعة أدناه ولا تخترع تواريخ أو وظائف غير مذكورة. '
            'إذا كانت المعلومة غير موجودة، قل ذلك بوضوح. اجعل الإجابة قصيرة ومناسبة لشاشة متحف.')
    context=json.dumps({'name':a['name_ar'],'age':a['age'],'location':a['location'],'material':a['material'],'description':a['description_ar'],'facts':a['facts'],'timeline':a['timeline']},ensure_ascii=False)
    payload={'model':model,'max_tokens':450,'system':system+'\nبيانات القطعة:\n'+context,'messages':[{'role':'user','content':q}]}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r=await client.post('https://api.anthropic.com/v1/messages',headers={'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json'},json=payload)
            r.raise_for_status(); data=r.json(); return ''.join(x.get('text','') for x in data.get('content',[]) if x.get('type')=='text').strip() or None
    except Exception:return None

def grounded_answer(a,q):
    ql=q.lower()
    if any(x in q for x in ['متى','تاريخ','العمر','الفترة']): return f"تعود القطعة إلى {a['age']}."
    if any(x in q for x in ['أين','الموقع','اكتشفت','عثر']): return f"يرتبط سياقها بموقع {a['location']}."
    if any(x in q for x in ['مادة','مصنوعة','صنعت']): return f"المادة المسجلة للقطعة هي {a['material']}."
    return a['story']+'\n\n'+a['description_ar']

@app.post('/chat')
async def chat(req:ChatRequest):
    a=BY_ID.get(req.artifact_id)
    if not a: raise HTTPException(404,'Artifact not found')
    answer=await llm_answer(a,req.question)
    agent='Ruwi LLM Agent' if answer else 'Ruwi Grounded Agent'
    return {'answer':answer or grounded_answer(a,req.question),'agent':agent}
