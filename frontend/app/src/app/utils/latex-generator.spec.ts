import { equationToLatex } from './latex-generator';

describe('equationToLatex', () => {
  it('renders signs correctly when equation payload uses numeric signs', () => {
    const latex = equationToLatex(
      {
        positions: { term1: 1, term2: 2, equals: 3, constant: 4 },
        term1: { sign: -1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 },
        term2: { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 },
        constant: { sign: 1, numCoeff: 5, numRad: 1, denCoeff: 1, denRad: 1 },
      },
      { var1: 'x', var2: 'y' }
    );

    expect(latex).toBe('-x + y = 5');
  });

  it('renders signs correctly when equation payload uses string signs', () => {
    const latex = equationToLatex(
      {
        positions: { term1: 1, term2: 2, equals: 3, constant: 4 },
        term1: { sign: '-' as unknown as 1 | -1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 },
        term2: { sign: '+' as unknown as 1 | -1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 },
        constant: { sign: 1, numCoeff: 5, numRad: 1, denCoeff: 1, denRad: 1 },
      },
      { var1: 'x', var2: 'y' }
    );

    expect(latex).toBe('-x + y = 5');
  });
});
