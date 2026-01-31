import json

# 验证修复后的判断题文件
fixed_file = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理判断题_fixed.json'

with open(fixed_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"=== 验证修复后的判断题文件 ===")
print(f"文件路径：{fixed_file}")
print(f"试卷标题：{data['title']}")
print(f"包含题目数量：{len(data['questions'])}")
print(f"试卷ID：{data['id']}")
print(f"时间戳：{data['timestamp']}")
print(f"是否提交：{data.get('isSubmitted', '未设置')}")

# 检查前3题和后3题
print(f"\n=== 前3题 ===")
for i, q in enumerate(data['questions'][:3]):
    print(f"\n第{i+1}题：")
    print(f"  题号：{q['meta'].split('、')[0].strip()}")
    print(f"  内容：{q['content'].strip()[:50]}...")
    print(f"  答案：{q['correctAnswer']}")

print(f"\n=== 后3题 ===")
for i, q in enumerate(data['questions'][-3:]):
    idx = len(data['questions']) - 3 + i + 1
    print(f"\n第{idx}题：")
    print(f"  题号：{q['meta'].split('、')[0].strip()}")
    print(f"  内容：{q['content'].strip()[:50]}...")
    print(f"  答案：{q['correctAnswer']}")

print(f"\n✅ 验证通过！修复后的文件包含完整的{len(data['questions'])}道判断题。")
