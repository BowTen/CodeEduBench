import requests
import json
import database_connect
import aitestOrm

session = database_connect.get_session('database_aitest')

# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)

judge_base_url = config['judge_api']['base_url']

def judge_code(problem_id, code):
	try:
		response = requests.post(judge_base_url + '/code', params={'problem_id': problem_id, 'code': code})
		
		# 检查HTTP状态码
		response.raise_for_status()  # 如果状态码不是200-299，会抛出HTTPError异常
		
		# 尝试获取pass_rate
		try:
			return response.json()['pass_rate']
		except KeyError:
			raise Exception(f"Invalid response format: {response.text}")  # 如果没有找到pass_rate，抛出异常
			
	except requests.exceptions.HTTPError as http_err:
		# 抛出 HTTP 错误
		raise Exception(f"HTTP error occurred: {http_err}, Response content: {response.text}")
	
	except requests.exceptions.RequestException as req_err:
		# 抛出请求错误
		raise Exception(f"Request error occurred: {req_err}")
	
	except Exception as e:
		# 其他异常
		raise Exception(f"Unexpected error: {str(e)}")

def judge_case(problem_id, cases):
	try:
		response = requests.post(judge_base_url + '/case', params={'problem_id': problem_id}, json=cases)
		
		# 检查HTTP状态码
		response.raise_for_status()  # 如果状态码不是200-299，会抛出HTTPError异常
		
		# 尝试获取pass_rate
		try:
			return response.json()['pass_rate']
		except KeyError:
			raise Exception(f"Invalid response format: {response.text}")  # 如果没有找到pass_rate，抛出异常
			
	except requests.exceptions.HTTPError as http_err:
		# 抛出 HTTP 错误
		raise Exception(f"HTTP error occurred: {http_err}, Response content: {response.text}")
	
	except requests.exceptions.RequestException as req_err:
		# 抛出请求错误
		raise Exception(f"Request error occurred: {req_err}")
	
	except Exception as e:
		# 其他异常
		raise Exception(f"Unexpected error: {str(e)}")


def judge_case_gen():
	case_gens = session.query(aitestOrm.CaseGen).filter(aitestOrm.CaseGen.correctness == None).filter(aitestOrm.CaseGen.comp_id != None).all()
	
	print("start_case_gen_judge, sum: ", len(case_gens))
	print('-' * 50)
	
	cnt = 0
	for case_gen in case_gens:
		try:
			test_cases = json.loads(case_gen.complement_gen.content)['test_case']
			data = {
				"test_cases": test_cases
			}
			
			# 调用judge_case，可能抛出异常
			pass_rate = judge_case(case_gen.problem_id, data)
			correctness = pass_rate * 5
			case_gen.correctness = correctness
			print("sc_id: ", case_gen.sc_id, "correctness: ", correctness)
			cnt += 1
		
		except Exception as e:
			print(f"sc_id: {case_gen.sc_id} - Error during judging: {e}")

		session.commit()

	print('-' * 50)
	print("end_case_gen_judge, success: ", cnt)

def judge_code_gen():
	code_gens = session.query(aitestOrm.CodeGen).filter(aitestOrm.CodeGen.correctness == None).filter(aitestOrm.CodeGen.comp_id != None).all()
	
	print("start_code_gen_judge, sum: ", len(code_gens))
	print('-' * 50)
	
	cnt = 0
	for code_gen in code_gens:
		try:
			code = json.loads(code_gen.complement_gen.content)['code']
			pass_rate = judge_code(code_gen.problem_id, code)
			correctness = pass_rate * 5
			code_gen.correctness = correctness
			print("sc_id: ", code_gen.sc_id, "correctness: ", correctness)
			cnt += 1
		except Exception as e:
			print(f"sc_id: {code_gen.sc_id} - Error during judging: {e}")
		
		session.commit()
	
	print('-' * 50)
	print("end_code_gen_judge, success: ", cnt)

def judge_code_cor():
	code_cors = session.query(aitestOrm.CodeCor).filter(aitestOrm.CodeCor.correctness == None).filter(aitestOrm.CodeCor.comp_id != None).all()
	
	print("start_code_cor_judge, sum: ", len(code_cors))
	print('-' * 50)

	cnt = 0
	for code_cor in code_cors:
		try:
			old_code = code_cor.code.code
			code = json.loads(code_cor.complement_gen.content)['code']
			
			# 获取老代码的通过率
			old_pass_rate = judge_code(code_cor.code.problem_for_code.problem_id, old_code)
			
			# 获取新代码的通过率
			pass_rate = judge_code(code_cor.code.problem_for_code.problem_id, code)
			
			#print("old_pass_rate: ", old_pass_rate, "pass_rate: ", pass_rate)
			# 计算correctness
			if old_pass_rate == 1.0:
				correctness = 0.0
			else:
				correctness = ((pass_rate - old_pass_rate) / (1.0 - old_pass_rate)) * 5
			if correctness < 0:
				correctness = 0.0
			code_cor.correctness = correctness
			print("sc_id: ", code_cor.sc_id, "correctness: ", correctness)
			cnt += 1
		except Exception as e:
			print(f"sc_id: {code_cor.sc_id} - Error during judging: {e}")

		session.commit()

	print('-' * 50)
	print("end_code_cor_judge, success: ", cnt)

def test():
	data = {
		"test_cases": [
			{
				"input": "1 2\n",
				"output": "3"
			},
			{
				"input": "3 2",
				"output": "5"
			},
			{
				"input": "3 2",
				"output": "5"
			}
		]
	}
	try:
		print(judge_case(1000, data))
	except Exception as e:
		print(e)

if __name__ == '__main__':
	judge_case_gen()
	judge_code_gen()
	judge_code_cor()

	#test()