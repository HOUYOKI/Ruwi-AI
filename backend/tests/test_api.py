from io import BytesIO
from PIL import Image
def auth(t):return {'Authorization':f'Bearer {t}'}
def test_health(client):assert client.get('/api/v1/health').status_code==200
def test_login_and_me(client,token):
 r=client.get('/api/v1/auth/me',headers=auth(token));assert r.status_code==200 and 'visitor' in r.json()['roles']
def test_registration(client):
 r=client.post('/api/v1/auth/register',json={'email':'new@example.com','password':'Secure123!','full_name':'New User','preferred_language':'en'});assert r.status_code==201
def test_role_permission(client,token,admin_token):
 assert client.get('/api/v1/admin/analytics',headers=auth(token)).status_code==403
 assert client.get('/api/v1/admin/analytics',headers=auth(admin_token)).status_code==200
def test_demo_artifacts(client):
 r=client.get('/api/v1/artifacts?language=ar');assert r.status_code==200 and r.json()['total']>=3
 slug=r.json()['items'][0]['slug'];d=client.get(f'/api/v1/artifacts/{slug}?language=en').json();assert d['stories'] and d['timeline'] and d['facts'] and d['hotspots'] and d['quizzes']
def test_upload_validation(client,token):
 r=client.post('/api/v1/uploads/artifact-image',headers=auth(token),files={'file':('bad.exe',b'bad','application/octet-stream')});assert r.status_code==415
 img=Image.new('RGB',(100,100));buf=BytesIO();img.save(buf,format='PNG');r=client.post('/api/v1/uploads/artifact-image',headers=auth(token),files={'file':('ok.png',buf.getvalue(),'image/png')});assert r.status_code==201
def test_ai_configuration_error(client,token):
 img=Image.new('RGB',(100,100));buf=BytesIO();img.save(buf,format='PNG');aid=client.post('/api/v1/uploads/artifact-image',headers=auth(token),files={'file':('ok.png',buf.getvalue(),'image/png')}).json()['analysis_id'];r=client.post(f'/api/v1/analyses/{aid}/start',headers=auth(token));assert r.status_code==503 and r.json()['detail']['code']=='AI_PROVIDER_NOT_CONFIGURED'
def test_planner(client):
 r=client.post('/api/v1/experience-plans?language=en&audience=student',json={'visual_characteristics':['handle']});assert r.status_code==200 and 'story' in r.json()['components']
def test_quiz_submission(client,token):
 a=client.get('/api/v1/artifacts?language=en').json()['items'][0];q=client.get(f"/api/v1/artifacts/{a['slug']}?language=en").json()['quizzes'][0];r=client.post(f"/api/v1/quizzes/{q['id']}/attempts",headers=auth(token),json=[1]);assert r.status_code==200 and r.json()['score']==1
def test_curator_edit_and_review(client,curator_token):
 a=client.get('/api/v1/artifacts').json()['items'][0];r=client.patch(f"/api/v1/curator/artifacts/{a['id']}",headers=auth(curator_token),json={'description_en':'Reviewed text'});assert r.status_code==200
