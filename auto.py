import os

# 定义不同参数的列表
list1 = [10, 100, 1000]
list2 = [1, 10, 100]
list3 = [0, 1e-6, 1e-5, 1e-4]

# 嵌套循环，遍历所有参数组合
for param1 in list1:
    for param2 in list2:
        for param3 in list3:
            # 构建运行main.py的命令，将参数作为命令行参数传递
            command1 = f"python go_back_N.py {param1} {param2} {param3}"
            command2 = f"python stop_and_wait.py {param1} {param2} {param3}"
            command3 = f"python selective_repeat.py {param1} {param2} {param3}"
            # 执行命令
            os.system(command1)
            os.system(command2)
            os.system(command3)
