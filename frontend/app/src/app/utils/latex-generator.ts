import { Term } from '../models/term.model';

type EquationVars = {
  var1?: string;
  var2?: string;
  variable1?: string;
  variable2?: string;
};

type EquationJson = {
  positions?: {
    term1?: number;
    term2?: number;
    equals?: number;
    constant?: number;
  };
  term1: Term;
  term2: Term;
  constant: Term;
  terms?: Term[];
};

type FrameKey = 'term1' | 'term2' | 'equals' | 'constant';

interface SignedExpressionTerm {
  sign: 1 | -1;
  value: string;
}

function normalizeSign(sign: unknown): 1 | -1 {
  if (sign === -1 || sign === '-1' || sign === '-' || sign === '−') {
    return -1;
  }

  return 1;
}

function sanitizePositiveInteger(value: number): number {
  const normalized = Number(value);

  if (!Number.isFinite(normalized) || normalized <= 0) {
    return 1;
  }

  return Math.floor(Math.abs(normalized));
}

function sanitizeNonNegativeInteger(value: number): number {
  const normalized = Number(value);

  if (!Number.isFinite(normalized) || normalized < 0) {
    return 0;
  }

  return Math.floor(Math.abs(normalized));
}

function buildUnsignedTerm(term: Term, options?: { allowZeroNumerator?: boolean }): string {
  const allowZeroNumerator = options?.allowZeroNumerator ?? false;
  const numCoeff = allowZeroNumerator
    ? sanitizeNonNegativeInteger(term.numCoeff)
    : sanitizePositiveInteger(term.numCoeff);

  if (allowZeroNumerator && numCoeff === 0) {
    return '0';
  }

  const numRad = sanitizePositiveInteger(term.numRad);
  const denCoeff = sanitizePositiveInteger(term.denCoeff);
  const denRad = sanitizePositiveInteger(term.denRad);

  let numerator = '';

  if (numCoeff !== 1) {
    numerator += `${numCoeff}`;
  }

  if (numRad !== 1) {
    numerator += `\\sqrt{${numRad}}`;
  }

  if (numerator === '') {
    numerator = '1';
  }

  let denominator = '';

  if (denCoeff !== 1) {
    denominator += `${denCoeff}`;
  }

  if (denRad !== 1) {
    denominator += `\\sqrt{${denRad}}`;
  }

  if (denominator === '') {
    return numerator;
  }

  return `\\frac{${numerator}}{${denominator}}`;
}

/**
 * Formats a variable coefficient (for x/y) without redundant 1.
 * Examples: 1 -> '', -1 -> '-' and √2 -> '\\sqrt{2}'.
 */
export function variableCoeffToLatex(term: Term): string {
  const unsigned = buildUnsignedTerm(term, { allowZeroNumerator: true });
  if (unsigned === '0') {
    return '0';
  }

  const signPrefix = normalizeSign(term.sign) === -1 ? '-' : '';

  if (unsigned === '1') {
    return signPrefix;
  }

  return `${signPrefix}${unsigned}`;
}

/**
 * Formats a constant term and always keeps 0/1 visible.
 * Examples: +1 -> '1', -1 -> '-1', 0 -> '0'.
 */
export function constantToLatex(term: Term): string {
  const unsigned = buildUnsignedTerm(term, { allowZeroNumerator: true });

  if (unsigned === '0') {
    return '0';
  }

  if (normalizeSign(term.sign) === -1) {
    return `-${unsigned}`;
  }

  return unsigned;
}

/**
 * Backward-compatible generic formatter.
 */
export function termToLatex(term: Term): string {
  return buildUnsignedTerm(term, { allowZeroNumerator: true });
}

export function equationToLatex(equation: EquationJson, variables: EquationVars): string {
  const normalized = normalizeEquation(equation);
  const positions = normalized.positions ?? { term1: 1, term2: 2, equals: 3, constant: 4 };
  const variable1 = extractVar(variables, 'first');
  const variable2 = extractVar(variables, 'second');

  const orderedKeys: FrameKey[] = (['term1', 'term2', 'equals', 'constant'] as FrameKey[]).sort(
    (a, b) => (positions[a] ?? 0) - (positions[b] ?? 0)
  );
  const equalsIndex = orderedKeys.indexOf('equals');
  const leftExpression = buildSide(normalized, orderedKeys.slice(0, equalsIndex), 'left', variable1, variable2);
  const rightExpression = buildSide(normalized, orderedKeys.slice(equalsIndex + 1), 'right', variable1, variable2);

  return `${leftExpression} = ${rightExpression}`;
}

function extractVar(variables: EquationVars, slot: 'first' | 'second'): string {
  const fromObject = slot === 'first' ? variables.var1 ?? variables.variable1 : variables.var2 ?? variables.variable2;
  if (fromObject) {
    return fromObject;
  }

  const fallback = (variables as unknown as { [key: string]: unknown })['variables'];
  if (Array.isArray(fallback)) {
    const value = fallback[slot === 'first' ? 0 : 1];
    if (typeof value === 'string' && value.trim()) {
      return value;
    }
  }

  return slot === 'first' ? 'x' : 'y';
}

function normalizeEquation(equation: EquationJson): EquationJson {
  const terms = Array.isArray(equation.terms) ? equation.terms : [];

  return {
    ...equation,
    term1: equation.term1 ?? terms[0],
    term2: equation.term2 ?? terms[1],
    constant: equation.constant
  };
}

function buildSide(
  equation: EquationJson,
  keys: FrameKey[],
  side: 'left' | 'right',
  variable1: string,
  variable2: string
): string {
  const terms = keys
    .map((key) => frameKeyToTerm(equation, key, side, variable1, variable2))
    .filter((term): term is SignedExpressionTerm => term !== null);

  return joinTerms(terms);
}

function frameKeyToTerm(
  equation: EquationJson,
  key: FrameKey,
  side: 'left' | 'right',
  variable1: string,
  variable2: string
): SignedExpressionTerm | null {
  if (key === 'equals') return null;

  if (key === 'constant') {
    const constantSign = normalizeSign(equation.constant.sign);
    const sign = side === 'left' ? (constantSign * -1) as 1 | -1 : constantSign;
    return { sign, value: constantToLatex({ ...equation.constant, sign: 1 }) };
  }

  if (key === 'term1') {
    const coeff = variableCoeffToLatex({ ...equation.term1, sign: 1 });
    if (coeff === '0') return null;
    return { sign: normalizeSign(equation.term1.sign), value: `${coeff}${variable1}` };
  }

  const coeff = variableCoeffToLatex({ ...equation.term2, sign: 1 });
  if (coeff === '0') return null;
  return { sign: normalizeSign(equation.term2.sign), value: `${coeff}${variable2}` };
}

function joinTerms(terms: SignedExpressionTerm[]): string {
  if (terms.length === 0) return '0';

  return terms
    .map((term, index) => {
      if (index === 0) return term.sign === -1 ? `-${term.value}` : term.value;
      return term.sign === -1 ? ` - ${term.value}` : ` + ${term.value}`;
    })
    .join('');
}
