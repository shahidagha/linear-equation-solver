export interface SolverStep {
  type?: string;
  content?: string;
  eq1?: string;
  eq2?: string;
  result?: string;
}

export interface MethodLatexPayload {
  latex_detailed: string;
  latex_medium: string;
  latex_short: string;
}

export type SolutionType = 'unique' | 'none' | 'infinite';

export interface SolverResponse {
  system_id?: number;
  /** Unique solution: { var1: value, var2: value }. Degenerate: null. */
  solution: Record<string, string | number> | null;
  /** Present when degenerate (no solution or infinitely many). */
  solution_type?: SolutionType;
  /** Human-readable conclusion when solution_type is 'none' or 'infinite'. */
  message?: string | null;
  methods: {
    elimination_latex?: MethodLatexPayload;
    substitution_latex?: MethodLatexPayload;
    cramer_latex?: MethodLatexPayload;
    graphical_latex?: MethodLatexPayload;
    [key: string]: unknown;
  };
  graph: {
    equation1_points: Array<[string | number, string | number]>;
    equation2_points: Array<[string | number, string | number]>;
    equation1_label?: string;
    equation2_label?: string;
    intersection: Record<string, string | number> | null;
    solution_type?: SolutionType;
    message?: string | null;
  };
}
