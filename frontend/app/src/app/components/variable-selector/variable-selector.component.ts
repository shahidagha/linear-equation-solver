import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-variable-selector',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './variable-selector.component.html',
  styleUrl: './variable-selector.component.css'
})
export class VariableSelectorComponent {

  variable1: string = 'x';
  variable2: string = 'y';

  validateVariable1() {

    this.variable1 = this.variable1.toLowerCase();

    if (!/[a-z]/.test(this.variable1)) {
      this.variable1 = '';
    }

    if (this.variable1 === this.variable2) {
      this.variable1 = '';
    }
  }

  validateVariable2() {

    this.variable2 = this.variable2.toLowerCase();

    if (!/[a-z]/.test(this.variable2)) {
      this.variable2 = '';
    }

    if (this.variable2 === this.variable1) {
      this.variable2 = '';
    }
  }

}