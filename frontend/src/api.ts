import type {Artifact,AgentRun} from './types'
const BASE=import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
async function get<T>(path:string):Promise<T>{const r=await fetch(BASE+path);if(!r.ok)throw new Error(await r.text());return r.json()}
export const api={
 artifacts:()=>get<Artifact[]>('/artifacts'),
 artifact:(id:number)=>get<Artifact>(`/artifacts/${id}`),
 agents:(id:number)=>get<AgentRun>(`/agents/${id}`),
 chat:async(id:number,question:string)=>{const r=await fetch(BASE+'/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artifact_id:id,question})});if(!r.ok)throw new Error(await r.text());return r.json() as Promise<{answer:string,agent:string}>}
}
