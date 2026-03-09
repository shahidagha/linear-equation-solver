import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InputPanelComponent } from './input-panel.component';

describe('InputPanelComponent', () => {
  let component: InputPanelComponent;
  let fixture: ComponentFixture<InputPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InputPanelComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InputPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
