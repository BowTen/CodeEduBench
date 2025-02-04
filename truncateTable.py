import database_connect
import aitestOrm
from sqlalchemy import text

session = database_connect.get_session('database_aitest')

def truncate_table(table):
	session.execute(text(f"DELETE FROM {table.__tablename__}"))
	session.commit()
	print(f"Truncate table {table.__tablename__} successfully.")


def truncate_prompt():
	truncate_table(aitestOrm.AnnotationGen)
	truncate_table(aitestOrm.KnlgExp)
	truncate_table(aitestOrm.CaseGen)
	truncate_table(aitestOrm.CodeGen)
	truncate_table(aitestOrm.CodeCor)
	truncate_table(aitestOrm.PromptComp)
	truncate_table(aitestOrm.ComplementGen)
	truncate_table(aitestOrm.PromptEval)
	truncate_table(aitestOrm.EvaluateGen)

def truncate_test_data():
	truncate_table(aitestOrm.Code)
	truncate_table(aitestOrm.ProblemForCode)
	truncate_table(aitestOrm.Problem)
	#truncate_table(aitestOrm.KnowledgePoint)
	truncate_table(aitestOrm.ModelScore)

def truncate_all():
	truncate_prompt()
	truncate_test_data()

if __name__ == '__main__':
	truncate_all()
	#truncate_prompt()