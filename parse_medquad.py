import os
import xml.etree.ElementTree as ET
import json

ROOT_FOLDER = "MedQuAD"
output = []

# Walk through all subfolders and collect XML files
for dirpath, _, filenames in os.walk(ROOT_FOLDER):
    for filename in filenames:
        if filename.endswith(".xml"):
            filepath = os.path.join(dirpath, filename)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()

                focus = root.findtext("Focus", default="General")

                for qa in root.findall(".//QAPair"):
                    question = qa.findtext("Question", "").strip()
                    answer = qa.findtext("Answer", "").strip()

                    if question and answer:
                        output.append({
                            "focus": focus,
                            "question": question,
                            "answer": answer
                        })

            except Exception as e:
                print(f"❌ Failed to parse {filename}: {e}")

# Save extracted Q&A to JSON
with open("medquad_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print(f"✅ Extracted {len(output)} Q&A pairs from {ROOT_FOLDER}")
