import json
from datetime import datetime

# 读取文件内容
with open(r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 提取判断题部分
judge_section = text.split('第一题：判断对错')[1].split('第二题：选择题')[0]

# 将文本按行分割
lines = judge_section.strip().split('\n')

print(f"判断题部分共有 {len(lines)} 行")

judge_questions = []

# 状态机变量
current_num = None  # 当前题目号
current_content = []  # 当前题目内容

for line in lines:
    line = line.strip()
    if not line:  # 跳过空行
        continue
    
    # 检查是否是题号行
    if line.startswith('(') or line.startswith('（'):
        # 保存上一题（如果有的话）
        if current_num is not None and current_content:
            # 提取答案
            answer = None
            for i, content_line in enumerate(current_content):
                if content_line in ['√', '×']:
                    answer = content_line
                    # 移除答案行
                    current_content.pop(i)
                    break
            
            if answer:
                # 合并题目内容
                content = ' '.join(current_content).strip()
                
                question = {
                    "id": len(judge_questions),
                    "type": "single",
                    "content": f"\n          <p><span>{current_num}.</span>&nbsp; <span>{content}</span></p>\n        ",
                    "options": [
                        {"label": "正确(True)", "html": "正确(True)"},
                        {"label": "错误(False)", "html": "错误(False)"}
                    ],
                    "correctAnswer": "正确(True)" if answer == "√" else "错误(False)",
                    "userAnswer": "",
                    "explanation": "",
                    "meta": f"\n          {current_num}、判断题（1分）\n          分值：1分\n          难度：适中\n        "
                }
                judge_questions.append(question)
        
        # 解析新的题目号
        if line.startswith('('):
            # 格式：(1) 数据库系统的一个主要特点是数据无冗余。
            num_end = line.find(')')
            if num_end != -1:
                current_num = line[1:num_end].strip()
                # 提取题目内容的第一部分
                content_part = line[num_end + 1:].strip()
                current_content = [content_part] if content_part else []
        elif line.startswith('（'):
            # 格式：（14）假设某同学年龄为30岁...
            num_end = line.find('）')
            if num_end != -1:
                current_num = line[1:num_end].strip()
                # 提取题目内容的第一部分
                content_part = line[num_end + 1:].strip()
                current_content = [content_part] if content_part else []
    
    # 检查是否是答案行
    elif line in ['√', '×']:
        if current_num is not None:
            current_content.append(line)
    
    # 否则是题目内容的一部分
    else:
        if current_num is not None:
            current_content.append(line)

# 保存最后一题
if current_num is not None and current_content:
    # 提取答案
    answer = None
    for i, content_line in enumerate(current_content):
        if content_line in ['√', '×']:
            answer = content_line
            current_content.pop(i)
            break
    
    if answer:
        content = ' '.join(current_content).strip()
        question = {
            "id": len(judge_questions),
            "type": "single",
            "content": f"\n          <p><span>{current_num}.</span>&nbsp; <span>{content}</span></p>\n        ",
            "options": [
                {"label": "正确(True)", "html": "正确(True)"},
                {"label": "错误(False)", "html": "错误(False)"}
            ],
            "correctAnswer": "正确(True)" if answer == "√" else "错误(False)",
            "userAnswer": "",
            "explanation": "",
            "meta": f"\n          {current_num}、判断题（1分）\n          分值：1分\n          难度：适中\n        "
        }
        judge_questions.append(question)

print(f"\n=== 解析结果 ===")
print(f"共解析成功 {len(judge_questions)} 道题")
print(f"成功解析的题号：{[q['meta'].split('、')[0].strip() for q in judge_questions]}")

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
