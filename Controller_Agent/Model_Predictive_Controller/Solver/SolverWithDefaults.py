from pyomo.environ import SolverFactory

def create_solver(solver_name, default_tee=False, **default_options):
    """
    Create a solver with a default tee option and safely configure options.
    
    :param solver_name: Name of the solver (e.g., 'glpk', 'gurobi').
    :param default_tee: Default value for the 'tee' parameter in solve calls.
    :param default_options: Additional solver-specific options to set during initialization.
    :return: Solver object with defaults pre-set.
    """
    class SolverWithDefaults:
        def __init__(self, solver_name, default_tee, default_options):
            self.solver = SolverFactory(solver_name)
            self.default_tee = default_tee
            
            # Set only the options supported by the solver
            for key, value in default_options.items():
                if self.solver.has_option(key):
                    self.solver.options[key] = value

        def set_option(self, key, value):
            """
            Safely set an option if supported by the solver.
            
            :param key: Option name.
            :param value: Option value.
            """
            if self.solver.has_option(key):
                self.solver.options[key] = value
            else:
                print(f"Warning: Solver '{solver_name}' does not support option '{key}'.")

        def solve(self, model, tee=None, **solve_options):
            """
            Solve the model using the solver, with the default tee value if not provided.
            
            :param model: The Pyomo model to solve.
            :param tee: Boolean to enable solver output.
            :param solve_options: Additional options for the solve method.
            :return: Solver results.
            """
            if tee is None:
                tee = self.default_tee
            return self.solver.solve(model, tee=tee, **solve_options)

    return SolverWithDefaults(solver_name, default_tee, default_options)

# # Example usage
# solver = create_solver('glpk', default_tee=False, mipgap=0.01)
# solver.set_option('timelimit', 300)  # Set an option later
# solver.set_option('nonexistent_option', 1)  # Unsupported option triggers a warning
# results = solver.solve(model)