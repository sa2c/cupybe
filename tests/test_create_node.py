#!/usr/bin/env python3
import calltree as ct
import pytest

line_simple = '    |-MPI_Finalize  [ ( id=163,   mod=), -1, -1, paradigm=mpi, role=function, url=, descr=, mode=MPI]'
line_cpp =    '    |-virtual SolverPetsc::~SolverPetsc()  [ ( id=163,   mod=), 13, 20, paradigm=compiler, role=function, url=, descr=, mode=/lustrehome/home/s.engkadac/cfdsfemmpi/src/base/SolverPetsc.cpp]'
line_cpp_templates = '    |-void Eigen::internal::call_dense_assignment_loop(const DstXprType&, const SrcXprType&, const Functor&) [with DstXprType = Eigen::Matrix<double, -1, -1, 1>; SrcXprType = Eigen::Matrix<double, -1, -1>; Functor = Eigen::internal::assign_op<double>]  [ ( id=163,   mod=), 632, 646, paradigm=compiler, role=function, url=, descr=, mode=/lustrehome/home/s.engkadac/mylibs/eigen-devel/Eigen/src/Core/AssignEvaluator.h]'

line_main = 'int main(int, char**)  [ ( id=1,   mod=), 22, 89, paradigm=compiler, role=function, url=, descr=, mode=/lustrehome/home/s.engkadac/cfdsfemmpi/src/cfdsfemmpi.cpp]'


lines = [ line_simple , line_cpp  , line_cpp_templates,]
funs = [ ct.create_node_simple, ct.create_node_cpp, ct.create_node_cpp_template ,]

def test_cnode_id():
    for l,f in zip(lines,funs):
        node = f(l)
        assert node.cnode_id == 163

@pytest.mark.parametrize('f',[ct.create_node_simple,ct.create_node])
def test_simple_node(f):
    node_simple = f(line_simple)
    assert node_simple.fname == "MPI_Finalize"

@pytest.mark.parametrize('f',[ct.create_node_cpp,ct.create_node])
def test_node_cpp(f):
    node_cpp = f(line_cpp)
    assert node_cpp.fname == "SolverPetsc::~SolverPetsc"
    assert node_cpp.fname_full == "virtual SolverPetsc::~SolverPetsc()"

@pytest.mark.parametrize('f',[ct.create_node_cpp,ct.create_node])
def test_node_main(f):
    node_main = f(line_main)
    assert node_main.fname == "main"
    assert node_main.fname_full == "int main(int, char**)"
    assert node_main.cnode_id == 1

@pytest.mark.parametrize('f',[ct.create_node_cpp_template,ct.create_node])
def test_node_cpp_template(f):
    node_cpp_template = f(line_cpp_templates)
    assert node_cpp_template.fname == "Eigen::internal::call_dense_assignment_loop"
    assert node_cpp_template.fname_full == "void Eigen::internal::call_dense_assignment_loop(const DstXprType&, const SrcXprType&, const Functor&)" 
    assert node_cpp_template.template_subs["DstXprType"] == "Eigen::Matrix<double, -1, -1, 1>"
    assert node_cpp_template.template_subs["SrcXprType"] == "Eigen::Matrix<double, -1, -1>"
    assert node_cpp_template.template_subs["Functor"] == "Eigen::internal::assign_op<double>"

