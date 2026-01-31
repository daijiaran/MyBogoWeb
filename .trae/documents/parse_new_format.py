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
        # 匹配格式：(1) 内容
        # × 或者 （1）内容
        # ×
        pattern = r'[\(（](\d+)[\)）]\s+(.*?)\n([√×])'
        matches = re.findall(pattern, judge_text, re.DOTALL)
        
        for i, (num, content, answer) in enumerate(matches):
            question = {
                "id": i,
                "type": "single",  # 注意：新格式中判断题的type也是"single"
                "content": f"\n          <p><span>{num}.</span>&nbsp; <span>{content.strip()}</span></p>\n        ",
                "options": [
                    {
                        "label": "正确(True)",
                        "html": "正确(True)"
                    },
                    {
                        "label": "错误(False)",
                        "html": "错误(False)"
                    }
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
    if single_section:
        single_text = single_section.group(1)
        
        # 分割成单个题目
        # 识别题目开头：（数字）或直接内容
        question_starts = re.finditer(r'（(\d+)）\s+|数据库三级模式', single_text)
        question_parts = []
        last_pos = 0
        
        for match in question_starts:
            pos = match.start()
            if pos > last_pos:
                question_parts.append(single_text[last_pos:pos])
            last_pos = pos
        
        question_parts.append(single_text[last_pos:])
        
        # 处理每个题目部分
        question_num = 1
        for part in question_parts:
            if not part.strip():
                continue
                
            # 检查是否包含答案（A、B、C、D）
            answer_match = re.search(r'\n([ABCD])\n', part)
            if not answer_match:
                continue
                
            answer = answer_match.group(1)
            
            # 提取题目内容
            content_match = re.search(r'(.*?)\nA\.?\s+', part, re.DOTALL)
            if not content_match:
                continue
                
            content = content_match.group(1).strip()
            # 移除题目编号
            content = re.sub(r'^（\d+）\s+', '', content)
            
            # 提取选项
            a_match = re.search(r'A\.?\s+(.*?)\nB\.?\s+', part, re.DOTALL)
            b_match = re.search(r'B\.?\s+(.*?)\nC\.?\s+', part, re.DOTALL)
            c_match = re.search(r'C\.?\s+(.*?)\nD\.?\s+', part, re.DOTALL)
            d_match = re.search(r'D\.?\s+(.*?)\n[ABCD]\n', part, re.DOTALL)
            
            if not all([a_match, b_match, c_match, d_match]):
                continue
                
            a = a_match.group(1).strip()
            b = b_match.group(1).strip()
            c = c_match.group(1).strip()
            d = d_match.group(1).strip()
            
            question = {
                "id": len(single_questions),
                "type": "single",
                "content": f"\n          <p>{content}</p>\n        ",
                "options": [
                    {
                        "label": "A",
                        "html": f"  {a}"
                    },
                    {
                        "label": "B",
                        "html": f"  {b}"
                    },
                    {
                        "label": "C",
                        "html": f"  {c}"
                    },
                    {
                        "label": "D",
                        "html": f"  {d}"
                    }
                ],
                "correctAnswer": answer,
                "userAnswer": "",
                "explanation": "",
                "meta": f"\n          {question_num}、单选题（1分）\n          分值：1分\n          难度：适中\n        "
            }
            single_questions.append(question)
            question_num += 1
    
    return single_questions

def main():
    # 读取temp.txt文件
    with open('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\documents\\temp.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 解析判断题
    judge_questions = parse_judge_questions(text)
    print(f"解析到判断题：{len(judge_questions)}道")
    
    # 解析单选题
    single_questions = parse_single_questions(text)
    print(f"解析到单选题：{len(single_questions)}道")
    
    # 生成判断题试卷
    judge_exam = {
        "id": f"{int(datetime.now().timestamp() * 1000)}",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "title": "数据库原理判断题",
        "questions": judge_questions
    }
    
    # 生成单选题试卷
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
