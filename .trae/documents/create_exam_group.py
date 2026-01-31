import json
import os

# 读取判断题和单选题文件
true_false_path = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理判断题.json'
single_choice_path = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理单选题.json'

# 读取文件内容
with open(true_false_path, 'r', encoding='utf-8') as f:
    true_false_exam = json.load(f)

with open(single_choice_path, 'r', encoding='utf-8') as f:
    single_choice_exam = json.load(f)

# 为每个试卷添加isSubmitted字段
true_false_exam['isSubmitted'] = True
single_choice_exam['isSubmitted'] = True

# 创建试卷组
exam_group = [true_false_exam, single_choice_exam]

# 写入到新文件
output_path = r'c:\Users\DAI\IdeaProjects\vue_project_2\.trae\数据库原理试卷组.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(exam_group, f, ensure_ascii=False, indent=2)

print(f"试卷组已创建：{output_path}")
print(f"包含 {len(exam_group)} 份试卷")
print(f"第一份试卷：{true_false_exam['title']}，共 {len(true_false_exam['questions'])} 道题")
print(f"第二份试卷：{single_choice_exam['title']}，共 {len(single_choice_exam['questions'])} 道题")
