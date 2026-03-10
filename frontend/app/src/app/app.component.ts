import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SavedSystemsComponent } from './components/saved-systems/saved-systems.component';
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, SavedSystemsComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'app';
}
