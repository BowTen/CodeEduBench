from genPrompt import generate_prompt
from runComplement import run_complement
from genEvaluatePrompt import generate_evaluate_prompt
from runEvaluate import run_evaluate
from judge import judge_case_gen, judge_code_gen, judge_code_cor
from summary import summary


if __name__ == '__main__':
	#1 抽取数据，初始化数据库（手动操作）


	#2 生成提示词（让模型生成内容）
	generate_prompt()
	#3 运行提示词
	run_complement()
	#4 生成提示词（为模型打分）
	generate_evaluate_prompt()
	#5 运行提示词
	run_evaluate()
	#6 调用评测机测试通过率
	judge_case_gen()
	judge_code_gen()
	judge_code_cor()
	#7 分数汇总
	summary()