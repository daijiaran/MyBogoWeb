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
    
    # 获取所有题号
    all_numbers = re.findall(r'[\(（](\d+)[\)）]', judge_text)
    
    print(f"找到 {len(all_numbers)} 个题号：{all_numbers}")
    
    judge_questions = []
    
    for expected_num in range(1, 36):  # 手动遍历1到35题
        expected_num_str = str(expected_num)
        
        # 搜索当前题号的题目
        # 尝试不同的括号格式
        patterns = [
            f'\({expected_num_str}\)',  # (1)
            f'（{expected_num_str}）'   # （1）
        ]
        
        found = False
        
        for pattern in patterns:
            # 找到当前题号的位置
            pos = judge_text.find(pattern)
            if pos != -1:
                found = True
                
                # 提取从当前题号到下一个题号或文本结束的内容
                next_pos = len(judge_text)
                
                # 查找下一个题号
                for next_num in range(expected_num + 1, 36):
                    next_patterns = [
                        f'\({next_num}\)',
                        f'（{next_num}）'
                    ]
                    for next_pat in next_patterns:
                        np = judge_text.find(next_pat, pos + 1)
                        if np != -1 and np < next_pos:
                            next_pos = np
                            break
                    if next_pos != len(judge_text):
                        break
                
                # 提取当前题目的内容
                current_content = judge_text[pos:next_pos]
                
                # 从内容中提取题目文本和答案
                content_match = re.search(r'[\)）]\s+(.+?)\n([√×])', current_content, re.DOTALL)
                
                if content_match:
                    content = content_match.group(1).strip()
                    answer = content_match.group(2)
                    
                    question = {
                        "id": len(judge_questions),
                        "type": "single",
                        "content": f"\n          <p><span>{expected_num}.</span>&nbsp; <span>{content}</span></p>\n        ",
                        "options": [
                            {"label": "正确(True)", "html": "正确(True)"},
                            {"label": "错误(False)", "html": "错误(False)"}
                        ],
                        "correctAnswer": "正确(True)" if answer == "√" else "错误(False)",
                        "userAnswer": "",
                        "explanation": "",
                        "meta": f"\n          {expected_num}、判断题（1分）\n          分值：1分\n          难度：适中\n        "
                    }
                    judge_questions.append(question)
                    print(f"✓ 成功解析第{expected_num}题")
                else:
                    print(f"✗ 无法解析第{expected_num}题的内容")
                    print(f"  题目内容：{current_content[:100]}...")
                
                break
        
        if not found:
            print(f"✗ 未找到第{expected_num}题")
    
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
