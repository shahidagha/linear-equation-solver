import { Term } from './term.model';

export interface Equation {

  term1: Term;
  term2: Term;
  constant: Term;

}