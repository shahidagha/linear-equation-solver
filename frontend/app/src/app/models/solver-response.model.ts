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

export interface SolverResponse {
  system_id?: number;
  solution: Record<string, string | number>;
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
    intersection: Record<string, string | number>;
  };
}
