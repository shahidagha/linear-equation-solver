import { Term } from '../models/term.model';

export function termToLatex(term: Term): string {

  let numerator = '';

  if (term.numCoeff !== 1) {
    numerator += term.numCoeff;
  }

  if (term.numRad !== 1) {
    numerator += `\\sqrt{${term.numRad}}`;
  }

  if (numerator === '') numerator = '1';

  let denominator = '';

  if (term.denCoeff !== 1) {
    denominator += term.denCoeff;
  }

  if (term.denRad !== 1) {
    denominator += `\\sqrt{${term.denRad}}`;
  }

  if (denominator === '') {
    return numerator;
  }

  return `\\frac{${numerator}}{${denominator}}`;
}