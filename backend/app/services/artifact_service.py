def artifact_dict(a,language="en",include_experience=True):
    ar=language=="ar"
    data={"id":a.id,"slug":a.slug,"title":a.title_ar if ar else a.title_en,"title_ar":a.title_ar,"title_en":a.title_en,"description":a.description_ar if ar else a.description_en,"category":(a.category.name_ar if ar else a.category.name_en) if a.category else None,"historical_period":a.historical_period_ar if ar else a.historical_period_en,"estimated_date":a.estimated_date_ar if ar else a.estimated_date_en,"origin":a.origin_ar if ar else a.origin_en,"material":a.material_ar if ar else a.material_en,"confidence":a.confidence,"verification_status":a.verification_status,"review_status":a.review_status,"is_demo":a.is_demo,"is_published":a.is_published,"image_url":a.image_url}
    if include_experience:
        data["stories"]=[{"id":s.id,"language":s.language,"audience":s.audience,"title":s.title,"content":s.content,"verified":s.verified} for s in a.stories]
        data["timeline"]=[{"id":e.id,"year":e.year_label_ar if ar else e.year_label_en,"title":e.title_ar if ar else e.title_en,"description":e.description_ar if ar else e.description_en} for e in sorted(a.timeline_events,key=lambda x:x.sort_order)]
        data["facts"]=[{"id":f.id,"text":f.text_ar if ar else f.text_en,"verified":f.verified} for f in a.facts]
        data["hotspots"]=[{"id":h.id,"x":h.x,"y":h.y,"label":h.label_ar if ar else h.label_en,"description":h.description_ar if ar else h.description_en} for h in a.hotspots]
        data["quizzes"]=[{"id":q.id,"language":q.language,"title":q.title,"questions":[{"id":x.id,"question":x.question,"choices":x.choices,"explanation":x.explanation,"difficulty":x.difficulty} for x in q.questions]} for q in a.quizzes if q.language==language]
    return data
