import re

# 读取文件内容
with open(r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 提取判断题部分
judge_section = re.search(r'第一题：判断对错(.*?)第二题：选择题', text, re.DOTALL)
if judge_section:
    judge_text = judge_section.group(1)
    print(f"判断题部分长度：{len(judge_text)}字符")
    print(f"判断题部分内容前500字符：\n{judge_text[:500]}...")
    print(f"\n判断题部分内容后500字符：\n{judge_text[-500:]}...")
    
    # 尝试不同的正则表达式
    patterns = [
        r'[\(（](\d+)[\)）]\s+(.*?)\n([√×])',
        r'[\(（](\d+)[\)）]\s+(.+?)\n([√×])',
        r'[\(（](\d+)[\)）]\s+(.{0,200}?)\n([√×])'
    ]
    
    for i, pattern in enumerate(patterns):
        matches = re.findall(pattern, judge_text, re.DOTALL)
        print(f"\n正则表达式 {i+1} 匹配到 {len(matches)} 个判断题")
        if len(matches) > 0:
            for j, match in enumerate(matches[:5]):  # 只显示前5个
                print(f"  {j+1}: 第{match[0]}题, 内容：{match[1][:20]}..., 答案：{match[2]}")
            if len(matches) > 5:
                print(f"  ... 还有 {len(matches) - 5} 个匹配")

        # 检查第20题附近的内容
        if len(matches) == 20:
            print(f"\n第20个匹配：")
            print(f"  题号：{matches[19][0]}")
            print(f"  内容：{matches[19][1]}")
            print(f"  答案：{matches[19][2]}")
            
            # 检查第20题之后的内容
            pos = judge_text.find(matches[19][1])
            if pos != -1:
                next_content = judge_text[pos + len(matches[19][1]) + 2:pos + len(matches[19][1]) + 100]
                print(f"  第20题之后的内容：{next_content}")
