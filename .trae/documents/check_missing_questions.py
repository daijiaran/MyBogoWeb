import re

# 读取文件内容
with open(r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\documents\temp.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 提取判断题部分
judge_section = re.search(r'第一题：判断对错(.*?)第二题：选择题', text, re.DOTALL)
if judge_section:
    judge_text = judge_section.group(1)
    
    print("=== 检查第12题到第23题之间的内容 ===")
    
    # 找到第12题的位置
    q12_pos = judge_text.find("（12）概念模型独立于硬件设备和DBMS。")
    if q12_pos != -1:
        # 提取第12题之后的1000个字符
        after_q12 = judge_text[q12_pos:q12_pos + 1000]
        print(after_q12)
        
        # 搜索所有题号
        all_numbers = re.findall(r'[\(（](\d+)[\)）]', judge_text)
        print(f"\n=== 所有找到的题号 ===")
        print(f"共找到 {len(all_numbers)} 个题号")
        print(f"题号列表：{all_numbers}")
        
        # 检查缺失的题号
        actual_numbers = sorted([int(num) for num in all_numbers])
        expected_numbers = list(range(1, 36))  # 1到35题
        
        missing = [num for num in expected_numbers if num not in actual_numbers]
        print(f"\n=== 缺失的题号 ===")
        print(f"缺失：{missing}")
        print(f"总共有 {len(expected_numbers)} 道题，找到 {len(actual_numbers)} 道题")
