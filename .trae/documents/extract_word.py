from docx import Document
import re

def extract_text_from_word():
    doc = Document('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\documents\\数据库原理作业选择.docx')
    full_text = []
    for para in doc.paragraphs:
        text = para.text
        if text.strip():
            full_text.append(text)
    return '\n'.join(full_text)

text = extract_text_from_word()
print(text)
with open('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\documents\\temp.txt', 'w', encoding='utf-8') as f:
    f.write(text)
