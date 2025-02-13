from database_connect import get_session
import aitestOrm
from tabulate import tabulate

session = get_session('database_aitest')


def summary():
    print("\nAI打分")
    models = session.query(aitestOrm.ModelScore).all()
    table_data = []  # 用于存储每个模型的评分数据

    for model in models:
        anno_gen_sc = 0
        for ann_gen in model.annotation_gens:
            anno_gen_sc += (ann_gen.accuracy + \
                                  ann_gen.simplicity + \
                                  ann_gen.naturalness + \
                                  ann_gen.usefulness) / 4
        anno_gen_sc /= len(model.annotation_gens)

        knlg_exp_sc = 0
        for knlg_exp in model.knlg_exps:
            knlg_exp_sc += (knlg_exp.accuracy + \
                                  knlg_exp.correlation + \
                                  knlg_exp.understandability) / 3
        knlg_exp_sc /= len(model.knlg_exps)

        case_gen_sc = 0
        for case_gen in model.case_gens:
            case_gen_sc += (case_gen.correctness + \
                                  case_gen.comprehensive) / 2
        case_gen_sc /= len(model.case_gens)

        code_gen_sc = 0
        for code_gen in model.code_gens:
            code_gen_sc += (code_gen.correctness + \
                                  code_gen.readability + \
                                  code_gen.performance) / 3
        code_gen_sc /= len(model.code_gens)

        code_cor_sc = 0
        for code_cor in model.code_cors:
            code_cor_sc += (code_cor.correctness + \
                                  code_cor.understandability) / 2
        code_cor_sc /= len(model.code_cors)

        final_score = (float(anno_gen_sc) + \
                          float(knlg_exp_sc) + \
                          float(case_gen_sc) + \
                          float(code_gen_sc) + \
                          float(code_cor_sc)) / 5
        
        # 将模型和对应的评分存入表格数据
        table_data.append([
            model.model_name,  # 假设模型有一个 name 属性
            round(anno_gen_sc, 2),
            round(knlg_exp_sc, 2),
            round(case_gen_sc, 2),
            round(code_gen_sc, 2),
            round(code_cor_sc, 2),
            round(final_score, 2)
        ])

    # 使用 tabulate 生成 Markdown 表格
    headers = [
        "Model Name",
        "Annotation Gen Score",
        "Knowledge Exp Score",
        "Case Gen Score",
        "Code Gen Score",
        "Code Cor Score",
        "Final Score"
    ]
    markdown_table = tabulate(table_data, headers=headers, tablefmt="pipe")

    # 输出 Markdown 表格
    print(markdown_table)
        
def summary_for_manual():
    print("\n人工打分")
    models = session.query(aitestOrm.ModelScore).all()
    table_data = []  # 用于存储每个模型的评分数据

    for model in models:
        anno_gen_sc = 0
        for ann_gen in model.annotation_gens:
            anno_gen_sc += (ann_gen.maccuracy + \
                                  ann_gen.msimplicity + \
                                  ann_gen.mnaturalness + \
                                  ann_gen.musefulness) / 4
        anno_gen_sc /= len(model.annotation_gens)

        knlg_exp_sc = 0
        for knlg_exp in model.knlg_exps:
            knlg_exp_sc += (knlg_exp.maccuracy + \
                                  knlg_exp.mcorrelation + \
                                  knlg_exp.munderstandability) / 3
        knlg_exp_sc /= len(model.knlg_exps)

        case_gen_sc = 0
        for case_gen in model.case_gens:
            case_gen_sc += (case_gen.correctness + \
                                  case_gen.mcomprehensive) / 2
        case_gen_sc /= len(model.case_gens)

        code_gen_sc = 0
        for code_gen in model.code_gens:
            code_gen_sc += (code_gen.correctness + \
                                  code_gen.mreadability + \
                                  code_gen.mperformance) / 3
        code_gen_sc /= len(model.code_gens)

        code_cor_sc = 0
        for code_cor in model.code_cors:
            code_cor_sc += (code_cor.correctness + \
                                  code_cor.munderstandability) / 2
        code_cor_sc /= len(model.code_cors)

        final_score = (float(anno_gen_sc) + \
                          float(knlg_exp_sc) + \
                          float(case_gen_sc) + \
                          float(code_gen_sc) + \
                          float(code_cor_sc)) / 5

        # 将模型和对应的评分存入表格数据
        table_data.append([
            model.model_name,  # 假设模型有一个 name 属性
            round(anno_gen_sc, 2),
            round(knlg_exp_sc, 2),
            round(case_gen_sc, 2),
            round(code_gen_sc, 2),
            round(code_cor_sc, 2),
            round(final_score, 2)
        ])

    # 使用 tabulate 生成 Markdown 表格
    headers = [
        "Model Name",
        "Annotation Gen Score",
        "Knowledge Exp Score",
        "Case Gen Score",
        "Code Gen Score",
        "Code Cor Score",
        "Final Score"
    ]
    markdown_table = tabulate(table_data, headers=headers, tablefmt="pipe")

    # 输出 Markdown 表格
    print(markdown_table)

    
if __name__ == '__main__':
    summary()
    summary_for_manual()