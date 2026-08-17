export type TimelineItem=[string,string]
export type Artifact={
 id:number; name_ar:string; name_en:string; age:string; location:string; material:string; description_ar:string; story:string;
 facts:string[]; timeline:TimelineItem[]; experience:string; experience_type:string; prompt:string; image:string; model:string; source:string
}
export type AgentRun={curator:string; historian:string; experience_designer:string; narrator:string; recommended:string; experience_plan?:string; experience_script_ar?:string}
