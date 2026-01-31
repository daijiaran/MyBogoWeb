import re

# 读取文件内容
with open(r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 提取判断题部分
judge_section = re.search(r'第一题：判断对错(.*?)第二题：选择题', text, re.DOTALL)
if judge_section:
    judge_text = judge_section.group(1)
    
    print("=== 完整的判断题部分内容 ===")
    print(judge_text)
    
    # 搜索所有题号
    print(f"\n=== 所有找到的题号 ===")
    all_numbers = re.findall(r'[\(（](\d+)[\)）]', judge_text)
    print(f"共找到 {len(all_numbers)} 个题号")
    print(f"题号列表：{all_numbers}")
    
    # 统计每个题号出现的次数
    from collections import Counter
    count = Counter(all_numbers)
    print(f"\n=== 题号出现次数统计 ===")
    for num, cnt in sorted(count.items(), key=lambda x: int(x[0])):
        print(f"第{num}题: {cnt}次")
