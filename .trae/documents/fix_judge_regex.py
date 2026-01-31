import re

# 读取文件内容
with open(r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 提取判断题部分
judge_section = re.search(r'第一题：判断对错(.*?)第二题：选择题', text, re.DOTALL)
if judge_section:
    judge_text = judge_section.group(1)
    
    # 修复后的正则表达式，处理答案后面可能的空行
    # (?s) 启用 DOTALL 模式，让 . 匹配换行符
    # [\s\n]* 匹配答案后面可能的空格和换行符
    pattern = r'(?s)[\(（](\d+)[\)）]\s+(.*?)\n([√×])[\s\n]*'
    
    matches = re.findall(pattern, judge_text)
    
    print(f"修复后的正则表达式匹配到 {len(matches)} 个判断题")
    print(f"题号列表：{[match[0] for match in matches]}")
    
    # 显示所有匹配的题目
    for i, match in enumerate(matches):
        print(f"\n第{i+1}个匹配（实际题号{match[0]}）：")
        print(f"  内容：{match[1]}")
        print(f"  答案：{match[2]}")
