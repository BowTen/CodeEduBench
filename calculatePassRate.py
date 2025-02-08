from database_connect import get_session
from jolOrm import Problem, Solution
import math
from tabulate import tabulate

session = get_session('database')

problems = session.query(Problem).all()
problem_cnt = [0] * 101
code_cnt = [0] * 101
accode_cnt = [0] * 101
wacode_cnt = [0] * 101

for problem in problems:
    ac = session.query(Solution).filter(Solution.problem_id == problem.problem_id, Solution.result == 4, Solution.language == 0).count()
    if ac == 0:
        continue
    pass_rate = 0
    if problem.accepted > 0:
        pass_rate = problem.accepted / problem.submit
    pass_rate = math.floor(pass_rate * 100)
    problem_cnt[pass_rate] += 1
    code_cnt[pass_rate] += problem.submit
    accode_cnt[pass_rate] += problem.accepted
    wacode_cnt[pass_rate] += problem.submit - problem.accepted


def print_data(rng, only_sum=False):
    print(f'{rng}:')
    # Prepare data for tabular output
    problem_cnt_sum = 0
    code_cnt_sum = 0
    accode_cnt_sum = 0
    wacode_cnt_sum = 0
    table_data = []
    for i in rng:
        if not only_sum:
            table_data.append([f'{i}%', problem_cnt[i], code_cnt[i], accode_cnt[i], wacode_cnt[i]])
        problem_cnt_sum += problem_cnt[i]
        code_cnt_sum += code_cnt[i]
        accode_cnt_sum += accode_cnt[i]
        wacode_cnt_sum += wacode_cnt[i]


    # Add a row for totals
    table_data.append(['总计', problem_cnt_sum, code_cnt_sum, accode_cnt_sum, wacode_cnt_sum])

    # Print table using tabulate with 'pipe' format for Markdown
    headers = ['通过率', '题目数', '提交数', 'AC数', 'WA数']
    print(tabulate(table_data, headers=headers, tablefmt='pipe'))
    print('\n\n\n')

print_data(range(0, 101))

print_data(range(0, 31), 1)
print_data(range(31, 61), 1)
print_data(range(61, 101), 1)