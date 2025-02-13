from database_connect import get_session
import aitestOrm
from aitestOrm import AnnotationGen, KnlgExp, CaseGen, CodeGen, CodeCor
from tabulate import tabulate

session = get_session('database_aitest')

def format_to_two_decimal_places(value):
    return f"{value:.2f}"

def summary_AnnotationGen(model_name):
    av_anno = AnnotationGen(accuracy=0, simplicity=0, naturalness=0, usefulness=0, maccuracy=0, msimplicity=0, mnaturalness=0, musefulness=0)
    for anno in session.query(AnnotationGen).filter(AnnotationGen.model_name==model_name).all():
        av_anno.accuracy += anno.accuracy
        av_anno.simplicity += anno.simplicity
        av_anno.naturalness += anno.naturalness
        av_anno.usefulness += anno.usefulness
        av_anno.maccuracy += anno.maccuracy
        av_anno.msimplicity += anno.msimplicity
        av_anno.mnaturalness += anno.mnaturalness
        av_anno.musefulness += anno.musefulness
    count = session.query(AnnotationGen).filter(AnnotationGen.model_name==model_name).count()
    av_anno.accuracy /= count
    av_anno.simplicity /= count
    av_anno.naturalness /= count
    av_anno.usefulness /= count
    av_anno.maccuracy /= count
    av_anno.msimplicity /= count
    av_anno.mnaturalness /= count
    av_anno.musefulness /= count
    average = (av_anno.accuracy + av_anno.simplicity + av_anno.naturalness + av_anno.usefulness + av_anno.maccuracy + av_anno.msimplicity + av_anno.mnaturalness + av_anno.musefulness) / 8

    headers = ["Model Name", "accuracy", "simplicity", "naturalness", "usefulness", "maccuracy", "msimplicity", "mnaturalness", "musefulness", "average"]
    data = [[model_name, 
             format_to_two_decimal_places(av_anno.accuracy), 
             format_to_two_decimal_places(av_anno.simplicity), 
             format_to_two_decimal_places(av_anno.naturalness), 
             format_to_two_decimal_places(av_anno.usefulness), 
             format_to_two_decimal_places(av_anno.maccuracy), 
             format_to_two_decimal_places(av_anno.msimplicity), 
             format_to_two_decimal_places(av_anno.mnaturalness), 
             format_to_two_decimal_places(av_anno.musefulness), 
             format_to_two_decimal_places(average)]]
    print("AnnotationGen Score:")
    print(tabulate(data, headers, tablefmt="pipe"))

def summary_KnlgExp(model_name):
    av_knlg = KnlgExp(accuracy=0, correlation=0, understandability=0, maccuracy=0, mcorrelation=0, munderstandability=0)
    for knlg in session.query(KnlgExp).filter(KnlgExp.model_name==model_name).all():
        av_knlg.accuracy += knlg.accuracy
        av_knlg.correlation += knlg.correlation
        av_knlg.understandability += knlg.understandability
        av_knlg.maccuracy += knlg.maccuracy
        av_knlg.mcorrelation += knlg.mcorrelation
        av_knlg.munderstandability += knlg.munderstandability
    count = session.query(KnlgExp).filter(KnlgExp.model_name==model_name).count()
    av_knlg.accuracy /= count
    av_knlg.correlation /= count
    av_knlg.understandability /= count
    av_knlg.maccuracy /= count
    av_knlg.mcorrelation /= count
    av_knlg.munderstandability /= count
    average = (av_knlg.accuracy + av_knlg.correlation + av_knlg.understandability + av_knlg.maccuracy + av_knlg.mcorrelation + av_knlg.munderstandability) / 6

    headers = ["Model Name", "accuracy", "correlation", "understandability", "maccuracy", "mcorrelation", "munderstandability", "average"]
    data = [[model_name, 
             format_to_two_decimal_places(av_knlg.accuracy), 
             format_to_two_decimal_places(av_knlg.correlation), 
             format_to_two_decimal_places(av_knlg.understandability), 
             format_to_two_decimal_places(av_knlg.maccuracy), 
             format_to_two_decimal_places(av_knlg.mcorrelation), 
             format_to_two_decimal_places(av_knlg.munderstandability), 
             format_to_two_decimal_places(average)]]
    print("KnlgExp Score:")
    print(tabulate(data, headers, tablefmt="pipe"))

def summary_CaseGen(model_name):
    av_case = CaseGen(correctness=0, comprehensive=0, mcomprehensive=0)
    for case in session.query(CaseGen).filter(CaseGen.model_name==model_name).all():
        av_case.correctness += case.correctness
        av_case.comprehensive += case.comprehensive
        av_case.mcomprehensive += case.mcomprehensive
    count = session.query(CaseGen).filter(CaseGen.model_name==model_name).count()
    av_case.correctness /= count
    av_case.comprehensive /= count
    av_case.mcomprehensive /= count
    average = (float(av_case.correctness) + av_case.comprehensive + av_case.mcomprehensive) / 3

    headers = ["Model Name", "correctness", "comprehensive", "mcomprehensive", "average"]
    data = [[model_name, 
             format_to_two_decimal_places(float(av_case.correctness)), 
             format_to_two_decimal_places(av_case.comprehensive), 
             format_to_two_decimal_places(av_case.mcomprehensive), 
             format_to_two_decimal_places(average)]]
    print("CaseGen Score:")
    print(tabulate(data, headers, tablefmt="pipe"))

def summary_CodeGen(model_name):
    av_code = CodeGen(correctness=0, readability=0, performance=0, mreadability=0, mperformance=0)
    for code in session.query(CodeGen).filter(CodeGen.model_name==model_name).all():
        av_code.correctness += code.correctness
        av_code.readability += code.readability
        av_code.performance += code.performance
        av_code.mreadability += code.mreadability
        av_code.mperformance += code.mperformance
    count = session.query(CodeGen).filter(CodeGen.model_name==model_name).count()
    av_code.correctness /= count
    av_code.readability /= count
    av_code.performance /= count
    av_code.mreadability /= count
    av_code.mperformance /= count
    average = (float(av_code.correctness) + av_code.readability + av_code.performance + av_code.mreadability + av_code.mperformance) / 5

    headers = ["Model Name", "correctness", "readability", "performance", "mreadability", "mperformance", "average"]
    data = [[model_name, 
             format_to_two_decimal_places(float(av_code.correctness)), 
             format_to_two_decimal_places(av_code.readability), 
             format_to_two_decimal_places(av_code.performance), 
             format_to_two_decimal_places(av_code.mreadability), 
             format_to_two_decimal_places(av_code.mperformance), 
             format_to_two_decimal_places(average)]]
    print("CodeGen Score:")
    print(tabulate(data, headers, tablefmt="pipe"))

def summary_CodeCor(model_name):
    av_codecor = CodeCor(correctness=0, understandability=0, munderstandability=0)
    for codecor in session.query(CodeCor).filter(CodeCor.model_name==model_name).all():
        av_codecor.correctness += codecor.correctness
        av_codecor.understandability += codecor.understandability
        av_codecor.munderstandability += codecor.munderstandability
    count = session.query(CodeCor).filter(CodeCor.model_name==model_name).count()
    av_codecor.correctness /= count
    av_codecor.understandability /= count
    av_codecor.munderstandability /= count
    average = (float(av_codecor.correctness) + av_codecor.understandability + av_codecor.munderstandability) / 3

    headers = ["Model Name", "correctness", "understandability", "munderstandability", "average"]
    data = [[model_name, 
             format_to_two_decimal_places(float(av_codecor.correctness)), 
             format_to_two_decimal_places(av_codecor.understandability), 
             format_to_two_decimal_places(av_codecor.munderstandability), 
             format_to_two_decimal_places(average)]]
    print("CodeCor Score:")
    print(tabulate(data, headers, tablefmt="pipe"))

if __name__ == '__main__':
    summary_AnnotationGen("Qwen2.5-Coder-7B-Instruct")
    print('\n\n')
    summary_KnlgExp("Qwen2.5-Coder-7B-Instruct")
    print('\n\n')
    summary_CaseGen("Qwen2.5-Coder-7B-Instruct")
    print('\n\n')
    summary_CodeGen("Qwen2.5-Coder-7B-Instruct")
    print('\n\n')
    summary_CodeCor("Qwen2.5-Coder-7B-Instruct")
    print('\n\n')



