import json

with open("data/artifacts.json", encoding="utf-8") as f:
    artifacts = json.load(f)

broken = [a["id"] for a in artifacts if "\\n" in a.get("ocr_arabic", "")]
print(f"{len(broken)} of {len(artifacts)} records have the double-escaped newline bug")
print("Affected ids:", broken)



#art_79 = next(a for a in artifacts if a["id"] == 45)
# print(art_79["ocr_arabic"])



with_hall = [a["id"] for a in artifacts if "قاعة" in a.get("ocr_arabic", "")]
line_counts = {a["id"]: a.get("ocr_arabic", "").count("\n") + 1 for a in artifacts}

print(f"{len(with_hall)} of {len(artifacts)} records mention a hall (قاعة)")
print(f"Line count range: {min(line_counts.values())} to {max(line_counts.values())}")


longest = max(artifacts, key=lambda a: a.get("ocr_arabic", "").count("\n"))
print(f"id {longest['id']}, {longest['ocr_arabic'].count(chr(10)) + 1} lines:\n")
print(longest["ocr_arabic"])