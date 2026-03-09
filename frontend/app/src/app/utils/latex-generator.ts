import { Term } from '../models/term.model';

function sanitizePositiveInteger(value: number): number {
  const normalized = Number(value);

  if (!Number.isFinite(normalized) || normalized <= 0) {
    return 1;
  }

  return Math.floor(Math.abs(normalized));
}

function buildUnsignedTerm(term: Term): string {
  const numCoeff = sanitizePositiveInteger(term.numCoeff);
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
  const unsigned = buildUnsignedTerm(term);
  const signPrefix = term.sign === -1 ? '-' : '';

  if (unsigned === '1') {
    return signPrefix;
  }

  return `${signPrefix}${unsigned}`;
}

/**
 * Formats a constant term and always keeps 1 visible.
 * Examples: +1 -> '1', -1 -> '-1'.
 */
export function constantToLatex(term: Term): string {
  const unsigned = buildUnsignedTerm(term);

  if (term.sign === -1) {
    return `-${unsigned}`;
  }

  return unsigned;
}

/**
 * Backward-compatible generic formatter.
 */
export function termToLatex(term: Term): string {
  return buildUnsignedTerm(term);
}
