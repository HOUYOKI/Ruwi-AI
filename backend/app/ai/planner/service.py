from app.schemas.ai import ExperiencePlan
class ExperiencePlanner:
    def plan(self,metadata:dict,knowledge:list,language:str,audience:str)->ExperiencePlan:
        available=bool(knowledge)
        components=["story","quick_facts","follow_up_chat"] if available else []
        skipped={}
        for item,ok in {"timeline":len(knowledge)>=2,"quiz":available,"hotspots":bool(metadata.get("visual_characteristics")),"narration":available}.items():
            if ok: components.append(item)
            else: skipped[item]="Insufficient grounded information"
        return ExperiencePlan(components=components,skipped=skipped,language=language,audience=audience)
