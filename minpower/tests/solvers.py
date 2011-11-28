'''Test the all of the solver links'''

from attest import Tests,assert_hook
from pympler.classtracker import ClassTracker
from pympler.classtracker_stats import HtmlStats
import objgraph
from minpower import optimization, config
solvers = Tests()
from coopr import pyomo
import logging
logging.basicConfig( level=logging.INFO, format='%(levelname)s: %(message)s')

tracker=ClassTracker()
for cls in [pyomo.ConcreteModel,pyomo.Var,pyomo.base.var._VarElement,
            pyomo.Constraint,optimization.Problem]:
    tracker.track_class(cls)

def simple_problem():
    prob=optimization.newProblem()
    tracker.create_snapshot('prob. init')
    x= optimization.new_variable('x',low=0,high=3)
    y= optimization.new_variable('y',low=0,high=1)
    prob.add_variable(x)
    prob.add_variable(y)
    prob.add_objective(y-4*x)
    prob.add_constraint(optimization.new_constraint('',x+y<=2))
    tracker.create_snapshot('prob. created')
    return prob 



def test_one_solver(solver_name):
    prob=simple_problem()
    prob.solve(solver=solver_name)
    tracker.create_snapshot('prob. solved')
    status=prob.status
    del prob
    tracker.create_snapshot('prob. deleted')
    if solver_name=='glpk':
        tracker.stats.print_summary()
        #HtmlStats(tracker=tracker).create_html('profile-simple-problem.html')
        models_left=objgraph.by_type('ConcreteModel')
        logging.critical( models_left )
        objgraph.show_backrefs(models_left,filename='backrefs-simple-problem.png')
    return status

@solvers.test
def cplex():
    '''Test each available solver on a simple problem'''
    if 'cplex' in config.available_solvers:
        assert test_one_solver('cplex')

@solvers.test
def glpk():
    '''Test the glpk solver on a simple problem'''
    if 'glpk' in config.available_solvers:
        assert test_one_solver('glpk')

@solvers.test
def gurobi():
    '''Test the gurobi solver on a simple problem'''
    if 'gurobi' in config.available_solvers:
        assert test_one_solver('gurobi')
        
if __name__ == "__main__": solvers.run()