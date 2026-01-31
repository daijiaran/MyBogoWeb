import json
import re
from datetime import datetime

def parse_questions(text):
    questions = []
    
    # 解析判断题
    judge_pattern = r'\((\d+)\)\s+(.*?)\n([√×])'
    judge_matches = re.findall(judge_pattern, text, re.DOTALL)
    
    for i, (num, content, answer) in enumerate(judge_matches):
        question = {
            "id": i,
            "type": "judge",
            "content": f"<p>{content.strip()}</p>",
            "options": [],
            "correctAnswer": "√" if answer == "√" else "×",
            "userAnswer": "",
            "explanation": "",
            "meta": f"{num}. 判断题（1.0分）难度：中"
        }
        questions.append(question)
    
    # 解析选择题
    single_pattern = r'（(\d+)）\s+(.*?)\nA\.\s+(.*?)\nB\.\s+(.*?)\nC\.\s+(.*?)\nD\.\s+(.*?)\n([ABCD])'
    single_matches = re.findall(single_pattern, text, re.DOTALL)
    
    for i, (num, content, a, b, c, d, answer) in enumerate(single_matches):
        question = {
            "id": len(questions),
            "type": "single",
            "content": f"<p>{content.strip()}</p>",
            "options": [
                {"label": "A", "html": f"<p>{a.strip()}</p>"},
                {"label": "B", "html": f"<p>{b.strip()}</p>"},
                {"label": "C", "html": f"<p>{c.strip()}</p>"},
                {"label": "D", "html": f"<p>{d.strip()}</p>"}
            ],
            "correctAnswer": answer,
            "userAnswer": "",
            "explanation": "",
            "meta": f"{num}. 单选题（1.0分）难度：中"
        }
        questions.append(question)
    
    return questions

def main():
    # 读取提取的文本
    with open('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\documents\\temp.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 解析题目
    questions = parse_questions(text)
    
    # 创建试卷结构
    exam = {
        "id": f"{int(datetime.now().timestamp() * 1000)}",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "title": "数据库原理作业选择",
        "questions": questions,
        "isSubmitted": False
    }
    
    # 读取原JSON文件
    with open('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\documents\\题目格式.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 添加新试卷
    data.append(exam)
    
    # 保存到新文件
    output_path = 'c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理作业选择.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"转换完成，输出文件：{output_path}")

if __name__ == "__main__":
    main()
