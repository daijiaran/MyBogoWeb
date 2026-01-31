import re
import json
from datetime import datetime

# 读取文件内容
with open(r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 提取判断题部分
judge_section = re.search(r'第一题：判断对错(.*?)第二题：选择题', text, re.DOTALL)
if judge_section:
    judge_text = judge_section.group(1)
    
    print(f"判断题部分长度：{len(judge_text)}字符")
    
    # 新的正则表达式设计思路：
    # 1. 匹配题号：[\(（](\d+)[\)）]
    # 2. 匹配题目内容：(.*?) - 非贪婪匹配，直到遇到答案
    # 3. 匹配答案：\n([√×]) - 答案在单独的一行
    # 4. 使用 (?s) 启用 DOTALL 模式，让 . 匹配换行符
    # 5. 使用正向前瞻确保只匹配到下一个题号之前的内容
    
    # 首先获取所有题号的位置
    all_question_markers = list(re.finditer(r'[\(（](\d+)[\)）]', judge_text))
    
    judge_questions = []
    
    for i, marker in enumerate(all_question_markers):
        num = marker.group(1)
        start_pos = marker.start()
        
        # 确定题目内容的结束位置
        if i < len(all_question_markers) - 1:
            # 如果不是最后一题，结束位置是下一个题号的开始位置
            end_pos = all_question_markers[i + 1].start()
        else:
            # 如果是最后一题，结束位置是整个文本的结束
            end_pos = len(judge_text)
        
        # 提取当前题目的完整内容（包括答案）
        question_full = judge_text[start_pos:end_pos]
        
        # 从题目完整内容中提取题目文本和答案
        # 匹配题目文本：从题号开始，到答案之前
        content_match = re.search(r'[\)）]\s+(.*?)\n([√×])', question_full, re.DOTALL)
        
        if content_match:
            content = content_match.group(1).strip()
            answer = content_match.group(2)
            
            question = {
                "id": i,
                "type": "single",
                "content": f"\n          <p><span>{num}.</span>&nbsp; <span>{content}</span></p>\n        ",
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
    
    print(f"\n成功解析到 {len(judge_questions)} 个判断题")
    print(f"题号列表：{[q['meta'].split('、')[0].strip() for q in judge_questions]}")
    
    # 生成完整的试卷
    judge_exam = {
        "id": f"{int(datetime.now().timestamp() * 1000)}",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "title": "数据库原理判断题",
        "questions": judge_questions,
        "isSubmitted": True
    }
    
    # 输出到文件
    output_path = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理判断题_fixed.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(judge_exam, f, ensure_ascii=False, indent=2)
    
    print(f"\n修复后的判断题已输出到：{output_path}")
