from sqlalchemy import Column, Integer, String, Text, DateTime, SmallInteger, DECIMAL, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey


Base = declarative_base()

class Problem(Base):
    __tablename__ = 'problem'
    
    problem_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, default='')
    description = Column(Text)
    input = Column(Text)
    output = Column(Text)
    sample_input = Column(Text)
    sample_output = Column(Text)
    spj = Column(CHAR(1), nullable=False, default='0')
    hint = Column(Text)
    author = Column(String(30))
    source = Column(String(100))
    in_date = Column(DateTime)
    time_limit = Column(Integer, nullable=False, default=0)
    memory_limit = Column(Integer, nullable=False, default=0)
    defunct = Column(CHAR(1), nullable=False, default='N')
    accepted = Column(Integer, default=0)
    submit = Column(Integer, default=0)
    solved_user = Column(Integer, default=0)
    submit_user = Column(Integer)
    score = Column(DECIMAL(6, 2), default=100.00)
    tag1 = Column(String(250))
    tag2 = Column(String(250))
    tag3 = Column(String(250))
    problemset = Column(String(255))

    # 通过solution关系来获取相关的解题记录
    solutions = relationship("Solution", back_populates="problem")

    def __repr__(self):
        return f"<Problem(id={self.problem_id}, title={self.title})>"



class Solution(Base):
    __tablename__ = 'solution'
    
    solution_id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey('problem.problem_id'), default=0)
    user_id = Column(String(20), nullable=False)
    time = Column(Integer, nullable=False, default=0)
    memory = Column(Integer, nullable=False, default=0)
    in_date = Column(DateTime, nullable=False)
    result = Column(SmallInteger, nullable=False, default=0)
    language = Column(Integer, nullable=False, default=0)
    ip = Column(CHAR(15), nullable=False)
    contest_id = Column(Integer)
    valid = Column(Integer, nullable=False, default=1)
    num = Column(Integer, nullable=False, default=-1)
    code_length = Column(Integer, nullable=False, default=0)
    judgetime = Column(DateTime)
    pass_rate = Column(DECIMAL(2, 2), nullable=False, default=0.00)
    judger = Column(String(16), nullable=False, default='LOCAL')

    # 定义与Problem表的关系
    problem = relationship("Problem", back_populates="solutions")

    # 通过source_code关系来获取源代码
    source_code = relationship("SourceCode", back_populates="solution", uselist=False)

    def __repr__(self):
        return f"<Solution(id={self.solution_id}, user_id={self.user_id}, problem_id={self.problem_id})>"



class SourceCode(Base):
    __tablename__ = 'source_code'
    
    solution_id = Column(Integer, ForeignKey('solution.solution_id'), primary_key=True)
    source = Column(Text, nullable=False)

    # 通过solution关系来获取相关的解题记录
    solution = relationship("Solution", back_populates="source_code")

    def __repr__(self):
        return f"<SourceCode(solution_id={self.solution_id})>"