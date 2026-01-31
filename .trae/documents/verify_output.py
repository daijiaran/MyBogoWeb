import json

def verify_json_file(file_path, expected_title):
    """验证JSON文件格式是否正确"""
    print(f"\n验证文件：{file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查基本结构
    if not isinstance(data, dict):
        print("✗ 文件根结构不是字典")
        return False
    
    # 检查必要字段
    required_fields = ['id', 'timestamp', 'title', 'questions']
    for field in required_fields:
        if field not in data:
            print(f"✗ 缺少必要字段：{field}")
            return False
    
    # 检查title
    if data['title'] != expected_title:
        print(f"✗ title不匹配，预期：{expected_title}，实际：{data['title']}")
        return False
    
    # 检查questions数组
    if not isinstance(data['questions'], list):
        print("✗ questions不是数组")
        return False
    
    # 检查前几个题目的格式
    if data['questions']:
        for i, question in enumerate(data['questions'][:3]):
            print(f"\n题目 {i+1}：")
            print(f"  类型：{question['type']}")
            print(f"  内容：{question['content'][:50]}...")
            print(f"  选项数：{len(question['options'])}")
            print(f"  正确答案：{question['correctAnswer']}")
            
            # 检查选项格式
            for opt in question['options']:
                if 'label' not in opt or 'html' not in opt:
                    print("✗ 选项格式错误")
                    return False
    
    print(f"\n✓ 验证通过！共包含 {len(data['questions'])} 道题目")
    return True

def main():
    # 验证判断题
    judge_file = 'c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理判断题.json'
    verify_json_file(judge_file, '数据库原理判断题')
    
    # 验证单选题
    single_file = 'c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理单选题.json'
    verify_json_file(single_file, '数据库原理单选题')

if __name__ == "__main__":
    main()
