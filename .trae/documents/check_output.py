import json

# 读取生成的JSON文件
with open('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理作业选择.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 查找新添加的题目
db_exam = None
for exam in data:
    if exam['title'] == '数据库原理作业选择':
        db_exam = exam
        break

if db_exam:
    print(f"找到'数据库原理作业选择'试卷")
    print(f"ID: {db_exam['id']}")
    print(f"时间戳: {db_exam['timestamp']}")
    print(f"题目数量: {len(db_exam['questions'])}")
    print(f"是否提交: {db_exam['isSubmitted']}")
    
    # 打印前几个题目作为示例
    print("\n前3个题目示例:")
    for i, question in enumerate(db_exam['questions'][:3]):
        print(f"\n题目 {i+1}:")
        print(f"类型: {question['type']}")
        print(f"内容: {question['content']}")
        if question['options']:
            print(f"选项: {[opt['label'] + ': ' + opt['html'] for opt in question['options']]}")
        print(f"正确答案: {question['correctAnswer']}")
        print(f"元信息: {question['meta']}")
else:
    print("未找到'数据库原理作业选择'试卷")
