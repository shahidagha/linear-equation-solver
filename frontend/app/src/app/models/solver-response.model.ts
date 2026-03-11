export interface SolverStep {
  type?: string;
  content?: string;
  eq1?: string;
  eq2?: string;
  result?: string;
}

export interface SolverResponse {
  solution: Record<string, string | number>;
  methods: {
    elimination?: SolverStep[];
    graphical_steps?: string[];
    [key: string]: unknown;
  };
  graph: {
    equation1_points: Array<[string | number, string | number]>;
    equation2_points: Array<[string | number, string | number]>;
    intersection: Record<string, string | number>;
  };
}
