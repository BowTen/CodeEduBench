from database_connect import get_session
import aitestOrm

session = get_session('database_aitest')


def summary():
	print("\nStart summary\n")
	models = session.query(aitestOrm.ModelScore).all()

	for model in models:
		print(f"Model {model.model_name} summary")
		model.anno_gen_sc = 0
		for ann_gen in model.annotation_gens:
			model.anno_gen_sc += (ann_gen.accuracy + \
								  ann_gen.simplicity + \
								  ann_gen.naturalness + \
								  ann_gen.usefulness) / 4
		model.anno_gen_sc /= len(model.annotation_gens)

		model.knlg_exp_sc = 0
		for knlg_exp in model.knlg_exps:
			model.knlg_exp_sc += (knlg_exp.accuracy + \
								  knlg_exp.correlation + \
								  knlg_exp.understandability) / 3
		model.knlg_exp_sc /= len(model.knlg_exps)

		model.case_gen_sc = 0
		for case_gen in model.case_gens:
			model.case_gen_sc += (case_gen.correctness + \
								  case_gen.comprehensive) / 2
		model.case_gen_sc /= len(model.case_gens)

		model.code_gen_sc = 0
		for code_gen in model.code_gens:
			model.code_gen_sc += (code_gen.correctness + \
								  code_gen.readability + \
								  code_gen.performance) / 3
		model.code_gen_sc /= len(model.code_gens)

		model.code_cor_sc = 0
		for code_cor in model.code_cors:
			model.code_cor_sc += (code_cor.correctness + \
								  code_cor.understandability) / 2
		model.code_cor_sc /= len(model.code_cors)

		model.final_score = (float(model.anno_gen_sc) + \
						  float(model.knlg_exp_sc) + \
						  float(model.case_gen_sc) + \
						  float(model.code_gen_sc) + \
						  float(model.code_cor_sc)) / 5

		session.commit()
		print(f"Model {model.model_name} summary finished")
	print("\nSummary finished\n")
	
if __name__ == '__main__':
	summary()