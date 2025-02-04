from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

EASY = 65
MEDIUM = 90
HARD = 100


class ModelScore(Base):
	__tablename__ = 'model_score'
	model_name = Column(String(255), primary_key=True, nullable=False)
	anno_gen_sc = Column(DECIMAL(5, 2), nullable=True)
	knlg_exp_sc = Column(DECIMAL(5, 2), nullable=True)
	case_gen_sc = Column(DECIMAL(5, 2), nullable=True)
	code_gen_sc = Column(DECIMAL(5, 2), nullable=True)
	code_cor_sc = Column(DECIMAL(5, 2), nullable=True)
	final_score = Column(DECIMAL(5, 2), nullable=True)

	# 反向关系
	annotation_gens = relationship("AnnotationGen", back_populates="model_score")
	knlg_exps = relationship("KnlgExp", back_populates="model_score")
	case_gens = relationship("CaseGen", back_populates="model_score")
	code_gens = relationship("CodeGen", back_populates="model_score")
	code_cors = relationship("CodeCor", back_populates="model_score")


class Problem(Base):
	__tablename__ = 'problem'
	problem_id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String(200), nullable=False)
	description = Column(Text)
	input = Column(Text)
	output = Column(Text)
	sample_input = Column(Text)
	sample_output = Column(Text)
	spj = Column(String(1), default='0', nullable=False)
	hint = Column(Text)
	time_limit = Column(Integer, default=0, nullable=False)
	memory_limit = Column(Integer, default=0, nullable=False)
	difficulty = Column(Integer, default=0, nullable=False)

	# 反向关系
	case_gens = relationship("CaseGen", back_populates="problem")
	code_gens = relationship("CodeGen", back_populates="problem")

	def __init__(self, jol_problem):
		self.problem_id = jol_problem.problem_id
		self.title = jol_problem.title
		self.description = jol_problem.description
		self.input = jol_problem.input
		self.output = jol_problem.output
		self.sample_input = jol_problem.sample_input
		self.sample_output = jol_problem.sample_output
		self.spj = jol_problem.spj
		self.hint = jol_problem.hint
		self.time_limit = jol_problem.time_limit
		self.memory_limit = jol_problem.memory_limit
		if(jol_problem.score <= EASY):
			self.difficulty = 1
		elif(jol_problem.score <= MEDIUM):
			self.difficulty = 2
		else:
			self.difficulty = 3

	def full_description(self):
		return self.title + "\n" + self.description + "\n" + \
			"input\n" + self.input + "\n" + "output\n" + self.output + "\n" + \
			"sample_input\n" + ("None" if self.sample_input is None else self.sample_input) + "\n" + \
			"sample_output\n" + ("None" if self.sample_output is None else self.sample_output)


class ProblemForCode(Base):
	__tablename__ = 'problem_for_code'
	problem_id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String(200), nullable=False)
	description = Column(Text)
	input = Column(Text)
	output = Column(Text)
	sample_input = Column(Text)
	sample_output = Column(Text)
	spj = Column(String(1), default='0', nullable=False)
	hint = Column(Text)
	time_limit = Column(Integer, default=0, nullable=False)
	memory_limit = Column(Integer, default=0, nullable=False)
	difficulty = Column(Integer, default=0, nullable=False)

	# 反向关系
	codes = relationship("Code", back_populates="problem_for_code")

	def __init__(self, jol_problem):
		self.problem_id = jol_problem.problem_id
		self.title = jol_problem.title
		self.description = jol_problem.description
		self.input = jol_problem.input
		self.output = jol_problem.output
		self.sample_input = jol_problem.sample_input
		self.sample_output = jol_problem.sample_output
		self.spj = jol_problem.spj
		self.hint = jol_problem.hint
		self.time_limit = jol_problem.time_limit
		self.memory_limit = jol_problem.memory_limit
		if(jol_problem.score <= EASY):
			self.difficulty = 1
		elif(jol_problem.score <= MEDIUM):
			self.difficulty = 2
		else:
			self.difficulty = 3

	def full_description(self):
		return self.title + "\n" + self.description + "\n" + \
			"input\n" + self.input + "\n" + "output\n" + self.output + "\n" + \
			"sample_input\n" + ("None" if self.sample_input is None else self.sample_input) + "\n" + \
			"sample_output\n" + ("None" if self.sample_output is None else self.sample_output)


class Code(Base):
	__tablename__ = 'code'
	code_id = Column(Integer, primary_key=True, autoincrement=True)
	problem_id = Column(Integer, ForeignKey('problem_for_code.problem_id'), nullable=False)
	code = Column(Text, nullable=False)
	accepted = Column(Integer, default=0, nullable=False)

	# 反向关系
	problem_for_code = relationship("ProblemForCode", back_populates="codes")
	annotation_gens = relationship("AnnotationGen", back_populates="code")
	code_cors = relationship("CodeCor", back_populates="code")


class KnowledgePoint(Base):
	__tablename__ = 'knowledge_point'
	knlg_id = Column(Integer, primary_key=True, autoincrement=True)
	content = Column(Text, nullable=False)
	level = Column(Integer, nullable=False)

	# 反向关系
	knlg_exps = relationship("KnlgExp", back_populates="knowledge_point")


class ComplementGen(Base):
	__tablename__ = 'complement_gen'
	comp_id = Column(Integer, primary_key=True, autoincrement=True)
	content = Column(Text, nullable=False)

	# 反向关系
	prompt_comps = relationship("PromptComp", back_populates="complement_gen")
	annotation_gens = relationship("AnnotationGen", back_populates="complement_gen")
	knlg_exps = relationship("KnlgExp", back_populates="complement_gen")
	case_gens = relationship("CaseGen", back_populates="complement_gen")
	code_gens = relationship("CodeGen", back_populates="complement_gen")
	code_cors = relationship("CodeCor", back_populates="complement_gen")


class PromptComp(Base):
	__tablename__ = 'prompt_comp'
	prompt_id = Column(Integer, primary_key=True, autoincrement=True)
	prompt_json = Column(Text, nullable=False)
	comp_id = Column(Integer, ForeignKey('complement_gen.comp_id'), nullable=True)
	type = Column(Integer, nullable=False)
	sc_id = Column(Integer, nullable=False)

	# 反向关系
	complement_gen = relationship("ComplementGen", back_populates="prompt_comps")


class EvaluateGen(Base):
	__tablename__ = 'evaluate_gen'
	eval_id = Column(Integer, primary_key=True, autoincrement=True)
	content = Column(Text, nullable=False)

	# 反向关系
	prompt_evals = relationship("PromptEval", back_populates="evaluate_gen")


class PromptEval(Base):
	__tablename__ = 'prompt_eval'
	prompt_id = Column(Integer, primary_key=True, autoincrement=True)
	prompt_json = Column(Text, nullable=False)
	eval_id = Column(Integer, ForeignKey('evaluate_gen.eval_id'), nullable=True)
	type = Column(Integer, nullable=False)
	sc_id = Column(Integer, nullable=False)

	# 反向关系
	evaluate_gen = relationship("EvaluateGen", back_populates="prompt_evals")


class AnnotationGen(Base):
	__tablename__ = 'annotation_gen'
	sc_id = Column(Integer, primary_key=True, autoincrement=True)
	model_name = Column(String(255), ForeignKey('model_score.model_name'), nullable=False)
	code_id = Column(Integer, ForeignKey('code.code_id'), nullable=False)
	comp_id = Column(Integer, ForeignKey('complement_gen.comp_id'), nullable=True)
	accuracy = Column(Integer, nullable=True)
	simplicity = Column(Integer, nullable=True)
	naturalness = Column(Integer, nullable=True)
	usefulness = Column(Integer, nullable=True)
	maccuracy = Column(Integer, nullable=True)
	msimplicity = Column(Integer, nullable=True)
	mnaturalness = Column(Integer, nullable=True)
	musefulness = Column(Integer, nullable=True)

	# 反向关系
	model_score = relationship("ModelScore", back_populates="annotation_gens")
	code = relationship("Code", back_populates="annotation_gens")
	complement_gen = relationship("ComplementGen", back_populates="annotation_gens")


class KnlgExp(Base):
	__tablename__ = 'knlg_exp'
	sc_id = Column(Integer, primary_key=True, autoincrement=True)
	model_name = Column(String(255), ForeignKey('model_score.model_name'), nullable=False)
	knlg_id = Column(Integer, ForeignKey('knowledge_point.knlg_id'), nullable=False)
	comp_id = Column(Integer, ForeignKey('complement_gen.comp_id'), nullable=True)
	accuracy = Column(Integer, nullable=True)
	correlation = Column(Integer, nullable=True)
	understandability = Column(Integer, nullable=True)
	maccuracy = Column(Integer, nullable=True)
	mcorrelation = Column(Integer, nullable=True)
	munderstandability = Column(Integer, nullable=True)

	# 反向关系
	model_score = relationship("ModelScore", back_populates="knlg_exps")
	knowledge_point = relationship("KnowledgePoint", back_populates="knlg_exps")
	complement_gen = relationship("ComplementGen", back_populates="knlg_exps")


class CaseGen(Base):
	__tablename__ = 'case_gen'
	sc_id = Column(Integer, primary_key=True, autoincrement=True)
	model_name = Column(String(255), ForeignKey('model_score.model_name'), nullable=False)
	problem_id = Column(Integer, ForeignKey('problem.problem_id'), nullable=False)
	comp_id = Column(Integer, ForeignKey('complement_gen.comp_id'), nullable=True)
	correctness = Column(DECIMAL(5, 2), nullable=True)
	comprehensive = Column(Integer, nullable=True)
	mcomprehensive = Column(Integer, nullable=True)

	# 反向关系
	model_score = relationship("ModelScore", back_populates="case_gens")
	problem = relationship("Problem", back_populates="case_gens")
	complement_gen = relationship("ComplementGen", back_populates="case_gens")


class CodeGen(Base):
	__tablename__ = 'code_gen'
	sc_id = Column(Integer, primary_key=True, autoincrement=True)
	model_name = Column(String(255), ForeignKey('model_score.model_name'), nullable=False)
	problem_id = Column(Integer, ForeignKey('problem.problem_id'), nullable=False)
	comp_id = Column(Integer, ForeignKey('complement_gen.comp_id'), nullable=True)
	correctness = Column(DECIMAL(5, 2), nullable=True)
	readability = Column(Integer, nullable=True)
	performance = Column(Integer, nullable=True)
	mreadability = Column(Integer, nullable=True)
	mperformance = Column(Integer, nullable=True)

	# 反向关系
	model_score = relationship("ModelScore", back_populates="code_gens")
	problem = relationship("Problem", back_populates="code_gens")
	complement_gen = relationship("ComplementGen", back_populates="code_gens")


class CodeCor(Base):
	__tablename__ = 'code_cor'
	sc_id = Column(Integer, primary_key=True, autoincrement=True)
	model_name = Column(String(255), ForeignKey('model_score.model_name'), nullable=False)
	code_id = Column(Integer, ForeignKey('code.code_id'), nullable=False)
	comp_id = Column(Integer, ForeignKey('complement_gen.comp_id'), nullable=True)
	correctness = Column(DECIMAL(5, 2), nullable=True)
	understandability = Column(Integer, nullable=True)
	munderstandability = Column(Integer, nullable=True)

	# 反向关系
	model_score = relationship("ModelScore", back_populates="code_cors")
	code = relationship("Code", back_populates="code_cors")
	complement_gen = relationship("ComplementGen", back_populates="code_cors")