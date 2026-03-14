"""
Substitution method: solve one equation for one variable, substitute into the other,
solve for the remaining variable, then back-substitute.
Steps 1 (standardization) are done upstream. Steps 2-6 and verification (detailed only) are recorded here.
"""
import sympy as sp
from backend.utils.step_recorder import StepRecorder
from backend.latex.equation_formatter import EquationFormatter


class SubstitutionSolver:
    def __init__(self, system):
        self.system = system
        self.var1 = getattr(system, "var1", "x")
        self.var2 = getattr(system, "var2", "y")
        self.recorder = StepRecorder()
        self._x = sp.Symbol(self.var1)
        self._y = sp.Symbol(self.var2)
        a1 = system.eq1.a.to_sympy()
        b1 = system.eq1.b.to_sympy()
        c1 = system.eq1.c.to_sympy()
        a2 = system.eq2.a.to_sympy()
        b2 = system.eq2.b.to_sympy()
        c2 = system.eq2.c.to_sympy()
        self._eq1 = (a1, b1, c1)
        self._eq2 = (a2, b2, c2)

    def _eq_latex(self, a, b, c, var1=None, var2=None):
        var1 = var1 or self.var1
        var2 = var2 or self.var2
        return EquationFormatter.format_equation(a, b, c, var1, var2)

    def _expr_latex(self, expr):
        return sp.latex(sp.simplify(expr))

    # --- Step 2: Select equation and variable (prefer coeff ±1, else smallest |coeff|) ---
    def _list_simple_options(self):
        """List (eq_num, var_name, a, b, c) where that variable has coefficient 1 or -1."""
        options = []
        for eq_num, (a, b, c) in enumerate([self._eq1, self._eq2], 1):
            if abs(sp.simplify(a)) == 1:
                options.append((eq_num, self.var1, a, b, c))
            if abs(sp.simplify(b)) == 1:
                options.append((eq_num, self.var2, a, b, c))
        return options

    def _select_equation_and_variable(self):
        """
        Step 2 selection: prefer (eq, var) with coefficient ±1; if multiple, prefer simpler substitute;
        if none, choose (eq, var) with smallest |coeff|.
        Returns (eq_num, solve_for_var, other_var, a, b, c, chose_simple).
        chose_simple = True if we picked an option with coefficient ±1.
        """
        options = self._list_simple_options()
        if options:
            if len(options) == 1:
                eq_num, var_name, a, b, c = options[0]
                other = self.var2 if var_name == self.var1 else self.var1
                return (eq_num, var_name, other, a, b, c, True)
            best = None
            for eq_num, var_name, a, b, c in options:
                other_var = self.var2 if var_name == self.var1 else self.var1
                coeff = a if var_name == self.var1 else b
                other_coeff = b if var_name == self.var1 else a
                score = (abs(sp.simplify(coeff)), abs(sp.simplify(other_coeff)), eq_num, 0 if var_name == self.var1 else 1)
                if best is None or score < best[0]:
                    best = (score, eq_num, var_name, other_var, a, b, c)
            _, eq_num, var_name, other_var, a, b, c = best
            return (eq_num, var_name, other_var, a, b, c, True)
        best = None
        for eq_num, (a, b, c) in enumerate([self._eq1, self._eq2], 1):
            for var_name, coeff in [(self.var1, a), (self.var2, b)]:
                cost = abs(sp.simplify(coeff))
                other_var = self.var2 if var_name == self.var1 else self.var1
                key = (cost, eq_num, 0 if var_name == self.var1 else 1)
                if best is None or key < best[0]:
                    best = (key, eq_num, var_name, other_var, a, b, c)
        _, eq_num, var_name, other_var, a, b, c = best
        return (eq_num, var_name, other_var, a, b, c, False)

    def _solve_for_var(self, eq_num, var_name, other_var, a, b, c):
        """Solve a*var1 + b*var2 = c for var_name. Returns (expr, sym_var, other_sym)."""
        x, y = self._x, self._y
        lhs = a * x + b * y
        eq = sp.Eq(lhs, c)
        sym_var = x if var_name == self.var1 else y
        other_sym = y if var_name == self.var1 else x
        sol = sp.solve(eq, sym_var)
        if not sol:
            return None, sym_var, other_sym
        expr = sp.simplify(sol[0])
        return expr, sym_var, other_sym

    def _why_we_chose(self, eq_num, var_name, chose_simple, a, b, c):
        """Build explanation for detailed view: why we chose this equation and variable."""
        coeff = a if var_name == self.var1 else b
        coeff_abs = abs(sp.simplify(coeff))
        if chose_simple and coeff_abs == 1:
            return (
                f"We choose equation ({eq_num}) because {var_name} has coefficient 1 or -1, "
                f"so solving for {var_name} is simplest. Solving equation ({eq_num}) for {var_name}:"
            )
        if chose_simple:
            return (
                f"We choose equation ({eq_num}) because it gives a simpler expression when we solve for {var_name}. "
                f"Solving equation ({eq_num}) for {var_name}:"
            )
        return (
            f"We choose equation ({eq_num}) because it has the smallest coefficient for {var_name} "
            f"among the two equations, so we solve for {var_name}. Solving equation ({eq_num}) for {var_name}:"
        )

    def _steps_to_solve_for_var(self, a, b, c, sym_var, other_sym, expr, var_name):
        """
        Produce step-by-step algebra from a*x + b*y = c to sym_var = expr.
        Returns list of (detailed_explanation, equation_latex). Medium/short get only the equations.
        """
        steps = []
        other_coeff = a if sym_var == self._y else b
        coeff = b if sym_var == self._y else a
        # Full equation (no label) is added separately
        # Step: subtract other term from both sides
        other_term = other_coeff * other_sym
        rhs1 = sp.simplify(c - other_term)
        step1_latex = f"{sp.latex(coeff * sym_var)} = {self._expr_latex(rhs1)}"
        steps.append((
            f"Subtract {self._expr_latex(other_term)} from both sides to isolate the term in {var_name}.",
            step1_latex,
        ))
        # Step: divide both sides by coeff
        raw_expr = sp.simplify(rhs1 / coeff)
        step2_latex = f"{sp.latex(sym_var)} = {self._expr_latex(raw_expr)}"
        steps.append((
            f"Divide both sides by {self._expr_latex(coeff)} to solve for {var_name}.",
            step2_latex,
        ))
        if sp.simplify(raw_expr - expr) != 0:
            steps.append((
                "Simplify.",
                f"{sp.latex(sym_var)} = {self._expr_latex(expr)}",
            ))
        return steps

    def _record_solve_for(self, eq_num, var_name, expr, sym_var, a, b, c, chose_simple):
        """
        Record Step 2: (detailed) why we chose this equation; (all) equation again without label;
        then all algebra steps to get var = expr (detailed: with explanation per step; medium/short: calculation only).
        """
        short_line = f"Solving equation ({eq_num}) for {var_name}:"
        detailed_line = self._why_we_chose(eq_num, var_name, chose_simple, a, b, c)
        self.recorder.add({"short": short_line, "detailed": detailed_line, "medium": short_line})

        # Equation (1) or (2) again without label
        self.recorder.add_equation(self._eq_latex(a, b, c))

        # Algebra steps: detailed gets explanation + equation, medium/short get equation only
        other_sym = self._y if sym_var == self._x else self._x
        algebra_steps = self._steps_to_solve_for_var(a, b, c, sym_var, other_sym, expr, var_name)
        for detailed_text, eq_latex in algebra_steps:
            self.recorder.add({"detailed": detailed_text, "equation": eq_latex})
        # If the last step is not already var = expr (e.g. we only had "Divide" and raw_expr != expr), add final line
        final_latex = f"{sp.latex(sym_var)} = {self._expr_latex(expr)}"
        if not algebra_steps or algebra_steps[-1][1] != final_latex:
            self.recorder.add({"detailed": "", "equation": final_latex})

    def _record_substitute_into(self, eq_num, var_name, expr, substituted_latex):
        """Record Step 3: Substituting ... into Equation (M): and the equation."""
        self.recorder.add(f"Substituting {var_name} = {self._expr_latex(expr)} into Equation ({eq_num}):")
        self.recorder.add_equation(substituted_latex)

    def _record_solve_one_var_steps(self, var_sym, eq_lhs_eq_rhs_steps):
        """Record Step 4: each calculation step (text + equation)."""
        for text, eq_latex in eq_lhs_eq_rhs_steps:
            if text:
                self.recorder.add(text)
            self.recorder.add_equation(eq_latex)

    def _record_back_substitute(self, other_var, value, expr, sym_var, other_sym, result_value):
        """Record Step 5: Substituting other_var = value into sym_var = expr: and calculation steps."""
        sym_var_name = self.var1 if sym_var == self._x else self.var2
        self.recorder.add(f"Substituting {other_var} = {self._expr_latex(value)} into {sym_var_name} = {self._expr_latex(expr)}:")
        expr_latex = sp.latex(expr)
        val_latex = sp.latex(value)
        other_latex = sp.latex(other_sym)
        subst_display = expr_latex.replace(other_latex, f"({val_latex})")
        self.recorder.add_equation(f"{sp.latex(sym_var)} = {subst_display}")
        self.recorder.add_equation(f"{sp.latex(sym_var)} = {self._expr_latex(result_value)}")

    def _expand_solve_steps(self, one_var_eq, var_sym):
        """From one_var_eq (e.g. 5*y - 10 = 0), produce list of (text, equation_latex) steps."""
        steps = []
        eq = sp.simplify(one_var_eq)
        if eq.rhs != 0:
            eq = sp.Eq(sp.simplify(eq.lhs - eq.rhs), 0)
        lhs = eq.lhs
        if not lhs.has(var_sym):
            return steps
        # Collect terms: coeff*var + constant = 0
        expanded = sp.expand(lhs)
        coeff = expanded.coeff(var_sym)
        constant = expanded.subs(var_sym, 0)
        if constant != 0:
            steps.append((f"Simplify (collect terms):", f"{self._expr_latex(expanded)} = 0"))
            # constant to RHS
            new_rhs = sp.simplify(-constant)
            steps.append((f"Add {self._expr_latex(-constant)} to both sides:", f"{sp.latex(coeff * var_sym)} = {self._expr_latex(new_rhs)}"))
            if coeff != 1 and coeff != -1:
                steps.append((f"Divide both sides by {self._expr_latex(coeff)}:", f"{sp.latex(var_sym)} = {self._expr_latex(sp.simplify(new_rhs / coeff))}"))
            else:
                steps.append((None, f"{sp.latex(var_sym)} = {self._expr_latex(sp.simplify(new_rhs / coeff))}"))
        else:
            steps.append((None, f"{sp.latex(var_sym)} = 0"))
        return steps

    def solve(self):
        """Run substitution method; record steps 2-6 and verification (detailed only). Return solution dict or []."""
        eq_num, solve_for_var, other_var, a, b, c, chose_simple = self._select_equation_and_variable()
        # Which equation we substitute INTO (the other one)
        target_eq_num = 2 if eq_num == 1 else 1
        a_t, b_t, c_t = self._eq2 if target_eq_num == 2 else self._eq1

        expr, sym_var, other_sym = self._solve_for_var(eq_num, solve_for_var, other_var, a, b, c)
        if expr is None:
            return self._fallback_solve()

        # Step 2: intro (why we chose), equation again without label, then all algebra steps
        self._record_solve_for(eq_num, solve_for_var, expr, sym_var, a, b, c, chose_simple)

        # Step 3: substitute into target equation
        target_lhs = a_t * self._x + b_t * self._y
        target_eq = sp.Eq(target_lhs, c_t)
        substituted = target_eq.subs(sym_var, expr)
        substituted = sp.Eq(sp.simplify(substituted.lhs), sp.simplify(substituted.rhs))
        subst_latex = f"{self._expr_latex(substituted.lhs)} = {self._expr_latex(substituted.rhs)}"
        self._record_substitute_into(target_eq_num, solve_for_var, expr, subst_latex)

        # Step 4: solve for other_sym
        one_var_eq = sp.Eq(sp.simplify(substituted.lhs - substituted.rhs), 0)
        calc_steps = self._expand_solve_steps(one_var_eq, other_sym)
        sol_other = sp.solve(substituted, other_sym)
        if not sol_other:
            return self._fallback_solve()
        other_value = sp.simplify(sol_other[0])
        if not calc_steps:
            self.recorder.add_equation(f"{sp.latex(other_sym)} = {self._expr_latex(other_value)}")
        else:
            self._record_solve_one_var_steps(other_sym, calc_steps)

        # Step 5: back-substitute
        result_first = sp.simplify(expr.subs(other_sym, other_value))
        self._record_back_substitute(other_var, other_value, expr, sym_var, other_sym, result_first)

        # Step 6: solution is appended by renderer; add verification for detailed only
        self.recorder.add({
            "detailed": "Check: substitute solution into Equation (1) and Equation (2) to verify.",
            "medium": "",
            "short": "",
        })

        # Build solution dict
        if sym_var == self._x:
            return {self._x: result_first, self._y: other_value}
        return {self._x: other_value, self._y: result_first}

    def _fallback_solve(self):
        """When symbolic solve fails, use SymPy solve and still return solution (no steps)."""
        eq1 = sp.Eq(
            self._eq1[0] * self._x + self._eq1[1] * self._y,
            self._eq1[2],
        )
        eq2 = sp.Eq(
            self._eq2[0] * self._x + self._eq2[1] * self._y,
            self._eq2[2],
        )
        sol = sp.solve((eq1, eq2), (self._x, self._y), dict=True)
        if not sol:
            return []
        s = sol[0]
        return {self._x: sp.simplify(s[self._x]), self._y: sp.simplify(s[self._y])}
