import json
import os

# 文件路径
judge_file = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理判断题_fixed.json'
single_file = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理单选题.json'
output_file = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理试卷组_final.json'

# 检查文件是否存在
for file_path in [judge_file, single_file]:
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        exit(1)

print(f"读取判断题文件：{judge_file}")
print(f"读取单选题文件：{single_file}")

# 读取文件内容
with open(judge_file, 'r', encoding='utf-8') as f:
    judge_exam = json.load(f)

with open(single_file, 'r', encoding='utf-8') as f:
    single_exam = json.load(f)

# 确保包含isSubmitted字段
if 'isSubmitted' not in judge_exam:
    judge_exam['isSubmitted'] = True

if 'isSubmitted' not in single_exam:
    single_exam['isSubmitted'] = True

# 创建试卷组
exam_group = [judge_exam, single_exam]

# 写入到新文件
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(exam_group, f, ensure_ascii=False, indent=2)

print(f"\n=== 试卷组创建成功 ===")
print(f"输出文件：{output_file}")
print(f"包含试卷数量：{len(exam_group)}")
print(f"\n=== 试卷详情 ===")
for i, exam in enumerate(exam_group, 1):
    print(f"\n试卷 {i}：")
    print(f"  标题：{exam['title']}")
    print(f"  题目数量：{len(exam['questions'])}")
    print(f"  试卷ID：{exam['id']}")
    print(f"  时间戳：{exam['timestamp']}")
    print(f"  是否提交：{exam['isSubmitted']}")

print(f"\n✅ 试卷组封装完成！")
