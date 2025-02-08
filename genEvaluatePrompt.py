from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
import json
import aitestOrm
from database_connect import get_session

# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)

# 获取数据库连接
session = get_session('database_aitest')

# 创建openai客户端
eval_model = config['evaluate_model']['name']
eval_api_key = config['evaluate_model']['api_key']
eval_base_url = config['evaluate_model']['base_url']

client = OpenAI(
	api_key = eval_api_key,
	base_url = eval_base_url
)

def splicing_anno_gen_eval_prompt(problem_description, code):
	json_schema = {
		"accuracy": 2,
		"simplicity": 4,
		"naturalness": 3,
		"usefulness": 5
	}
	prompt = {
		"model": eval_model,
		"messages": [
			{"role": "system", "content": f"""你是一个代码注释审核以及C语言编程方面的专家。接下来你会被提供以下内容：
	(1)problem:C语言编程题目描述;
	(2)code:题目对应的带有注释的C代码；
	(3)standards:评估标准，包含代码注释质量的评估维度及其评估指标。你的任务是参考题目，根据评估标准对代码注释质量进行评估。
	请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}"""},
			{"role": "user", "content": f"""
	这是我提供的内容：
	problem:
	{problem_description}
	code:
	{code}
	standards:
	一、准确性(accuracy)：
	1 分：注释与代码的关键操作、核心功能和重要变量毫无关联，对理解代码毫无帮助，甚至严重误导对代码功能的判断。
	2 分：仅部分提及代码相关内容，但包含大量错误和偏差，只能大致反映代码意图，核心信息不准确。
	3 分：能反映代码主要功能，但存在遗漏或不准确之处，可让读者大致明白代码功能，但对部分细节不清楚。如计算平均值的函数，注释提及了平均值计算功能，但未说明特殊情况处理。
	4 分：准确反映代码功能及关键细节，仅存在少量不影响整体理解的小瑕疵，能有效辅助理解代码逻辑。例如复杂算法的注释，核心步骤描述准确，但个别变量含义解释不细致。
	5 分：精准、全面地反映代码意图，涵盖所有关键细节，与代码紧密相关，不仅帮助理解代码，还能提供优化方向等额外信息。像加密算法代码的注释，解释了加密流程及安全性考量和优化方向。
	二、简洁性(simplicity)：
	1 分：注释充斥大量语法错误、拼写错误，语句不通顺，严重影响阅读和理解，让人难以读懂。
	2 分：存在较多语法错误或语句结构混乱，主谓不一致、用词不当等，阅读时需花费大量精力梳理，影响整体感受。
	3 分：存在少量语法错误或语句稍不流畅，可能有标点使用不当、表述拗口等问题，但基本不影响理解，阅读会有短暂停顿。
	4 分：语法基本正确，语句通顺，文字流畅，符合正常表达习惯，能轻松阅读和理解。
	5 分：语法完全正确，语言简洁流畅，表达清晰准确，富有逻辑性和条理性，阅读体验好。
	三、自然性(naturalness)：
	1 分：注释有大量错误，包括语法、拼写和语句问题，读起来很不自然，难以理解其意思，如表述杂乱无章。
	2 分：较多语法和语句问题，主谓宾使用混乱，语言表达不自然，阅读困难，需费力理解。
	3 分：少量语法错误或语句不流畅，部分表述稍显生硬，阅读时会感到不自然，但不影响整体理解。
	4 分：语法基本正确，语句自然，符合正常语言表达习惯，阅读顺畅。
	5 分：语法正确，表达自然流畅，逻辑清晰，让人能快速理解注释含义。
	四、有用性(usefulness)：
	1 分：注释只是简单重复代码表面信息或与代码无关，对理解代码无价值，如仅重复函数名和参数名，无解释说明。
	2 分：仅提供少量基础信息，对深入理解代码帮助不大，如对复杂算法仅说明基本功能，不涉及核心逻辑。
	3 分：提供一定量信息，能辅助理解部分代码逻辑，但解释不全面，对工作原理和用途解释不足。例如对函数的注释仅提及部分功能，未解释关键步骤和参数作用。
	4 分：包含较多有助于理解的信息，能解释主要功能、基本逻辑和关键细节，但未涉及适用场景、潜在风险等。
	5 分：提供丰富且有深度的信息，涵盖功能、逻辑、实现思路，还提供背景知识、使用场景、优化方向和注意事项等，全面支持理解和使用代码。
	"""}
		],
		"response_format": {"type": "json_object"}
	}
	return json.dumps(prompt, ensure_ascii=False)

def splicing_knlg_exp_eval_prompt(knowledge_point_content, knowledge_point_exp):
	json_schema = {
		"accuracy": 2,
		"correlation": 4,
		"understandability": 3
	}
	prompt = {
		"model": eval_model,
		"messages": [
			{"role": "system", "content": f"""你是一个代码审核以及C语言编程方面的专家。接下来你会被提供以下内容：
	(1)knowledge:C语言语法点；
	(2)explanations:该语法点对应的案例解释；
	(3)standards:评估标准，包含语法点案例解释质量的评估维度及其评估指标。你的任务是参考语法点，根据评估标准对案例解释质量进行评估。
	请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}"""},
			{"role": "user", "content": f"""
	这是我提供的内容：
	knowledge:
	{knowledge_point_content}
	explanations:
	{knowledge_point_exp}
	standards:
	一、准确性(accuracy)：
	1 分：案例完全不符合语法点的官方定义和标准用法，代码示例存在严重错误，解释内容具有极大的误导性，基本无参考价值，严重干扰学生学习。
	2 分：案例存在较多错误，对语法点解释偏差明显，部分内容误导学生，学生难把握正确含义与用法，需大改。
	3 分：案例能大致体现语法点主要内容，但有小错误或解释不精确之处，会使学生产生困惑，经思考或指导可纠正。
	4 分：整体符合语法点要求，仅极个别细微瑕疵，不影响理解，基本无阻碍学生掌握知识。
	5 分：案例对语法点解释与官方定义、标准用法完全一致，代码示例遵循语法规则，各方面精准无误，提供可靠知识。
	二、相关性(correlation)：
	1 分：案例及解释与给定语法点关联度极低，多为无关信息，深度不适合学习阶段，无法助学生理解，需重新设计。
	2 分：案例与语法点有一定关联，但无关信息多或深度不符，使学生困惑，需大量删减或补充内容。
	3 分：案例和解释大部分相关，有偏离主题内容或深度不匹配情况，会分散注意力、增加理解难度，适当引导可抓重点。
	4 分：案例和解释与语法点高度相关，少量无关信息，深度符合要求，对理解和应用有较好帮助，细节可优化。
	5 分：案例及解释紧密围绕语法点，无无关信息，深度适配难度与学习阶段，对基础或复杂语法点呈现恰当，助力学生掌握。
	三、易懂性(understandability)：
	1 分：语言表达晦涩难懂，大量专业术语且无解释，结构混乱无逻辑，学生几乎无法理解语法规则与案例关系，需重编。
	2 分：语言晦涩，专业术语多且缺解释，结构不清晰，逻辑乱，学生理解困难，需教师或资料大量辅助。
	3 分：语言基本能懂，有一定专业术语，结构有一定条理，但逻辑衔接不紧密，学生需花时间精力梳理。
	4 分：语言较通俗易懂，专业术语少不影响理解，结构清晰，逻辑连贯，学生简单阅读就能理解关系，少量提示可掌握。
	5 分：语言极其通俗易懂，无专业术语或解释清晰，结构非常清晰，按先规则、再案例、后说明的方式，学生轻松理解，无需额外指导。
	"""}
		],
		"response_format": {"type": "json_object"}
	}
	return json.dumps(prompt, ensure_ascii=False)

def splicing_case_gen_eval_prompt(problem_description, case_json):
	json_schema = {
		"comprehensive": 2,
	}
	prompt = {
		"model": eval_model,
		"messages": [
			{"role": "system", "content": f"""你是一个代码测试以及C语言编程方面的专家。接下来你会被提供以下内容：
	(1)problem:C语言编程题目描述；
	(2)samples:题目对应的测试样例；
	(3)standards:评估标准，包含测试样例质量的评估维度及其评估指标。你的任务是参考题目，根据评估标准对测试样例质量进行评估。
	请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}"""},
			{"role": "user", "content": f"""
	这是我提供的内容：
	problem:
	{problem_description}
	samples:
	{case_json}
	standards:
	请你根据提供的编程题目和测试样例，按照以下标准对全面性维度进行打分：
	全面性(comprehensive)：测试样例能否覆盖题目的典型情况、边界情况和特殊情况。
	1分：样例覆盖率极低，缺少基本情况，完全不考虑边界条件。
	2分：样例覆盖了一部分常见输入，但未考虑边界情况或特殊情况。
	3分：样例覆盖了大部分常见输入，部分边界和特殊情况。
	4分：样例较全面，涵盖典型情况、常见边界条件，特殊情况覆盖少量缺失。
	5分：样例非常全面，涵盖了所有典型、边界和特殊情况，无明显遗漏。
	"""}],
		"response_format": {"type": "json_object"}
	}
	return json.dumps(prompt, ensure_ascii=False)

def splicing_code_gen_eval_prompt(problem_description, code):
	json_schema = {
		"readability": 2,
		"performance": 5
	}
	prompt = {
		"model": eval_model,
		"messages": [
			{"role": "system", "content": f"""你是一个代码审核以及C语言编程方面的专家。接下来你会被提供以下内容：
	(1)problem:C语言编程题目描述;
	(2)code:题目对应的C代码；
	(3)standards:评估标准，包含代码质量的评估维度及其评估指标。
	你的任务是参考题目，根据评估标准对代码质量进行评估。
	请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}"""},
			{"role": "user", "content": f"""
	这是我提供的内容：
	problem:
	{problem_description}
	code:
	{code}
	standards:
	请你根据提供的编程题目和代码，按照以下标准对每个维度进行打分：
	一、可读性(readability)：
	1分：代码完全缺乏可读性，变量名和函数名无语义，且没有注释或结构化设计。
	2分：代码部分可读，命名有一定意义，但注释较少且逻辑混乱，不易理解。
	3分：代码基本可读，命名清晰，注释覆盖常见逻辑，但部分结构仍不够清晰。
	4分：代码易于阅读和理解，命名规范，注释覆盖主要逻辑，结构较为清晰。
	5分：代码非常直观，命名语义明确，注释全面且简洁，结构清晰且模块化，无冗余逻辑。
	二、性能(performance)：	
	1分：时间和空间效率极差，运行时间远超题目限制，内存使用严重超出题目限制。
	2分：时间和空间效率较差，运行时间接近或略超题目限制，内存使用接近题目限制的上限。
	3分：时间和空间效率一般，运行时间接近题目限制，内存使用明显高于最优解但未超限。
	4分：时间和空间效率较高，运行时间稍高于最优解，但在合理范围内，内存使用接近题目限制。
	5分：时间和空间效率均非常高，运行时间接近最优解，内存使用远低于题目限制。
	"""}],
		"response_format": {"type": "json_object"}
	}
	return json.dumps(prompt, ensure_ascii=False)

def splicing_code_cor_eval_prompt(problem_description, code):
	json_schema = {
		"understandability": 2,
	}
	prompt = {
		"model": eval_model,
		"messages": [
			{"role": "system", "content": f"""你是一个代码审核以及C语言编程方面的专家。接下来你会被提供以下内容：
	(1)problem:C语言编程题目描述;
	(2)code:题目对应的纠错后的C代码；
	(3)standards:评估标准，包含纠错代码质量的评估维度及其评估指标。你的任务是参考题目，根据评估标准对纠错后代码质量进行评估。
	请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}"""},
			{"role": "user", "content": f"""
	这是我提供的内容：
	problem:
	{problem_description}
	code:
	{code}
	standards:
	请你根据提供的编程题目和代码，按照以下标准对易懂性维度进行打分：
	可理解性(understandability)：
	1 分：代码完全不可读，无任何注释或说明，关键逻辑缺失解释，未指出原始错误位置或原因，仅机械性修正代码。
	2 分：代码难以理解，仅有少量注释，仅解释简单操作，未覆盖关键算法，粗略提及错误位置，但无具体原因分析。
	3 分：代码基本可读，注释覆盖主要逻辑，但对复杂算法或边界条件解释不足，明确标注错误位置，并简要说明错误类型。
	4 分：代码高度清晰，注释详细解释核心算法、异常处理及关键参数设计，能结合上下文详细分析错误原因，说明修正策略。
	5 分：代码完美可读，注释精准覆盖全部复杂逻辑，包括性能优化与潜在风险说明，精准定位错误根源，提供错误归因与预防建议表 。
	"""}],
		"response_format": {"type": "json_object"}
	}
	return json.dumps(prompt, ensure_ascii=False)



def gen_anno_gen_eval_prompt():
	# 获取所有已生成complement的annotation_gen
	anno_gens = session.query(aitestOrm.AnnotationGen).filter(aitestOrm.AnnotationGen.comp_id != None).filter(aitestOrm.AnnotationGen.accuracy == None).all()
	cnt = 0
	for anno_gen in anno_gens:
		if session.query(aitestOrm.PromptEval).filter(aitestOrm.PromptEval.sc_id == anno_gen.sc_id).filter(aitestOrm.PromptEval.type == 1).first() is not None:
			continue
		problem_description = anno_gen.code.problem_for_code.full_description()
		code = anno_gen.complement_gen.content

		prompt_json = splicing_anno_gen_eval_prompt(problem_description, code)

		prompt = aitestOrm.PromptEval(
			prompt_json = prompt_json,
			type = 1,
			sc_id = anno_gen.sc_id
		)
		session.add(prompt)

		print(f"insert annotation_gen evaluation prompt for {anno_gen.sc_id}.")
		cnt += 1

	session.commit()
	print(f"insert {cnt} annotation_gen evaluation prompts.")

def gen_knlg_exp_eval_prompt():
	# 获取所有已生成complement的knowledge_exp
	knlg_exps = session.query(aitestOrm.KnlgExp).filter(aitestOrm.KnlgExp.comp_id != None).filter(aitestOrm.KnlgExp.accuracy == None).all()
	cnt = 0
	for knlg_exp in knlg_exps:
		if session.query(aitestOrm.PromptEval).filter(aitestOrm.PromptEval.sc_id == knlg_exp.sc_id).filter(aitestOrm.PromptEval.type == 2).first() is not None:
			continue
		knowledge_point_content = knlg_exp.knowledge_point.content
		knowledge_point_exp = knlg_exp.complement_gen.content

		prompt_json = splicing_knlg_exp_eval_prompt(knowledge_point_content, knowledge_point_exp)

		prompt = aitestOrm.PromptEval(
			prompt_json = prompt_json,
			type = 2,
			sc_id = knlg_exp.sc_id
		)
		session.add(prompt)

		print(f"insert knowledge_exp evaluation prompt for {knlg_exp.sc_id}.")
		cnt += 1

	session.commit()
	print(f"insert {cnt} knowledge_exp evaluation prompts.")

def gen_case_gen_eval_prompt():
	case_gens = session.query(aitestOrm.CaseGen).filter(aitestOrm.CaseGen.comp_id != None).filter(aitestOrm.CaseGen.comprehensive == None).all()
	cnt = 0
	for case_gen in case_gens:
		if session.query(aitestOrm.PromptEval).filter(aitestOrm.PromptEval.sc_id == case_gen.sc_id).filter(aitestOrm.PromptEval.type == 3).first() is not None:
			continue

		problem_description = case_gen.problem.full_description()
		case_json = case_gen.complement_gen.content

		prompt_json = splicing_case_gen_eval_prompt(problem_description, case_json)

		prompt = aitestOrm.PromptEval(
			prompt_json = prompt_json,
			type = 3,
			sc_id = case_gen.sc_id
		)
		session.add(prompt)

		print(f"insert case_gen evaluation prompt for {case_gen.sc_id}.")
		cnt += 1

	session.commit()
	print(f"insert {cnt} case_gen evaluation prompts.")

def gen_code_gen_eval_prompt():
	code_gens = session.query(aitestOrm.CodeGen).filter(aitestOrm.CodeGen.comp_id != None).filter(aitestOrm.CodeGen.readability == None).all()
	cnt = 0
	for code_gen in code_gens:
		if session.query(aitestOrm.PromptEval).filter(aitestOrm.PromptEval.sc_id == code_gen.sc_id).filter(aitestOrm.PromptEval.type == 4).first() is not None:
			continue
		
		problem_description = code_gen.problem.full_description()
		code = code_gen.complement_gen.content

		prompt_json = splicing_code_gen_eval_prompt(problem_description, code)

		prompt = aitestOrm.PromptEval(
			prompt_json = prompt_json,
			type = 4,
			sc_id = code_gen.sc_id
		)
		session.add(prompt)

		print(f"insert code_gen evaluation prompt for {code_gen.sc_id}.")
		cnt += 1

	session.commit()
	print(f"insert {cnt} code_gen evaluation prompts.")

def gen_code_cor_eval_prompt():
	code_cors = session.query(aitestOrm.CodeCor).filter(aitestOrm.CodeCor.comp_id != None).filter(aitestOrm.CodeCor.understandability == None).all()
	cnt = 0
	for code_cor in code_cors:
		if session.query(aitestOrm.PromptEval).filter(aitestOrm.PromptEval.sc_id == code_cor.sc_id).filter(aitestOrm.PromptEval.type == 5).first() is not None:
			continue

		problem_description = code_cor.code.problem_for_code.full_description()
		code = code_cor.complement_gen.content

		prompt_json = splicing_code_cor_eval_prompt(problem_description, code)

		prompt = aitestOrm.PromptEval(
			prompt_json = prompt_json,
			type = 5,
			sc_id = code_cor.sc_id
		)
		session.add(prompt)

		print(f"insert code_cor evaluation prompt for {code_cor.sc_id}.")
		cnt += 1

	session.commit()	
	print(f"insert {cnt} code_cor evaluation prompts.")


def generate_evaluate_prompt():
	gen_anno_gen_eval_prompt()
	gen_knlg_exp_eval_prompt()
	gen_case_gen_eval_prompt()
	gen_code_gen_eval_prompt()
	gen_code_cor_eval_prompt()


if __name__ == '__main__':
	gen_anno_gen_eval_prompt()
	gen_knlg_exp_eval_prompt()
	gen_case_gen_eval_prompt()
	gen_code_gen_eval_prompt()
	gen_code_cor_eval_prompt()