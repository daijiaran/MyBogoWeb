import json
import re
from datetime import datetime

def parse_judge_questions(text):
    """解析判断题"""
    judge_questions = []
    
    # 提取判断题部分
    judge_section = re.search(r'第一题：判断对错(.*?)第二题：选择题', text, re.DOTALL)
    if judge_section:
        judge_text = judge_section.group(1)
        
        # 匹配所有判断题
        pattern = r'[\(（](\d+)[\)）]\s+(.*?)\n([√×])'
        matches = re.findall(pattern, judge_text, re.DOTALL)
        
        for i, (num, content, answer) in enumerate(matches):
            question = {
                "id": i,
                "type": "single",
                "content": f"\n          <p><span>{num}.</span>&nbsp; <span>{content.strip()}</span></p>\n        ",
                "options": [
                    {"label": "正确(True)", "html": "正确(True)"},
                    {"label": "错误(False)", "html": "错误(False)"}
                ],
                "correctAnswer": "正确(True)" if answer == "√" else "错误(False)",
                "userAnswer": "",
                "explanation": "",
                "meta": f"\n          {num}、判断题（1分）\n          分值：1分\n          难度：适中\n        "
            }
            judge_questions.append(question)
    
    return judge_questions

def parse_single_questions(text):
    """解析单选题"""
    single_questions = []
    
    # 提取选择题部分
    single_section = re.search(r'第二题：选择题(.*?)', text, re.DOTALL)
    if not single_section:
        return single_questions
        
    single_text = single_section.group(1)
    
    # 手动处理每个题目，基于已知的题目结构
    # 观察到题目有（1）到（40）
    for question_num in range(1, 41):
        # 构建题目模式
        pattern = f"（{question_num}）\s+(.*?)\nA\.?\s+(.*?)\nB\.?\s+(.*?)\nC\.?\s+(.*?)\nD\.?\s+(.*?)\n([ABCD])"
        match = re.search(pattern, single_text, re.DOTALL)
        
        if match:
            content = match.group(1).strip()
            a = match.group(2).strip()
            b = match.group(3).strip()
            c = match.group(4).strip()
            d = match.group(5).strip()
            answer = match.group(6)
            
            question = {
                "id": len(single_questions),
                "type": "single",
                "content": f"\n          <p>{content}</p>\n        ",
                "options": [
                    {"label": "A", "html": f"  {a}"},
                    {"label": "B", "html": f"  {b}"},
                    {"label": "C", "html": f"  {c}"},
                    {"label": "D", "html": f"  {d}"}
                ],
                "correctAnswer": answer,
                "userAnswer": "",
                "explanation": "",
                "meta": f"\n          {question_num}、单选题（1分）\n          分值：1分\n          难度：适中\n        "
            }
            single_questions.append(question)
    
    # 处理特殊题目（数据库三级模式）
    special_pattern = r'数据库三级模式,反映了三种不同角度看待数据库的观点,用户眼中的数据库称为(     )。\nA\.?\s+(.*?)\nB\.?\s+(.*?)\nC\.?\s+(.*?)\nD\.?\s+(.*?)\nD'
    special_match = re.search(special_pattern, single_text, re.DOTALL)
    
    if special_match:
        content = "数据库三级模式,反映了三种不同角度看待数据库的观点,用户眼中的数据库称为(     )。"
        a = special_match.group(1).strip()
        b = special_match.group(2).strip()
        c = special_match.group(3).strip()
        d = special_match.group(4).strip()
        answer = "D"
        
        question = {
            "id": len(single_questions),
            "type": "single",
            "content": f"\n          <p>{content}</p>\n        ",
            "options": [
                {"label": "A", "html": f"  {a}"},
                {"label": "B", "html": f"  {b}"},
                {"label": "C", "html": f"  {c}"},
                {"label": "D", "html": f"  {d}"}
            ],
            "correctAnswer": answer,
            "userAnswer": "",
            "explanation": "",
            "meta": f"\n          11、单选题（1分）\n          分值：1分\n          难度：适中\n        "
        }
        single_questions.append(question)
    
    return single_questions

def main():
    # 读取temp.txt文件
    with open('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\documents\\temp.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 解析题目
    judge_questions = parse_judge_questions(text)
    single_questions = parse_single_questions(text)
    
    print(f"解析到判断题：{len(judge_questions)}道")
    print(f"解析到单选题：{len(single_questions)}道")
    
    # 生成试卷
    judge_exam = {
        "id": f"{int(datetime.now().timestamp() * 1000)}",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "title": "数据库原理判断题",
        "questions": judge_questions
    }
    
    single_exam = {
        "id": f"{int(datetime.now().timestamp() * 1000) + 1}",
        "timestamp": int(datetime.now().timestamp() * 1000) + 1,
        "title": "数据库原理单选题",
        "questions": single_questions
    }
    
    # 输出到文件
    judge_output_path = 'c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理判断题.json'
    single_output_path = 'c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理单选题.json'
    
    with open(judge_output_path, 'w', encoding='utf-8') as f:
        json.dump(judge_exam, f, ensure_ascii=False, indent=2)
    
    with open(single_output_path, 'w', encoding='utf-8') as f:
        json.dump(single_exam, f, ensure_ascii=False, indent=2)
    
    print(f"\n判断题输出到：{judge_output_path}")
    print(f"单选题输出到：{single_output_path}")

if __name__ == "__main__":
    main()
