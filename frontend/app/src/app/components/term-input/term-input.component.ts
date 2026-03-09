import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Term } from '../../models/term.model';

@Component({
  selector: 'app-term-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './term-input.component.html',
  styleUrl: './term-input.component.css'
})
export class TermInputComponent {

  term: Term = {
    sign: 1,
    numCoeff: 1,
    numRad: 1,
    denCoeff: 1,
    denRad: 1
  };

  @Output() termChange = new EventEmitter<Term>();

  updateTerm() {
    console.log("Term changed:", this.term);
    this.termChange.emit(this.term);
  }

}