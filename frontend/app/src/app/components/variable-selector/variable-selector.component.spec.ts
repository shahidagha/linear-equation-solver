import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VariableSelectorComponent } from './variable-selector.component';

describe('VariableSelectorComponent', () => {
  let component: VariableSelectorComponent;
  let fixture: ComponentFixture<VariableSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VariableSelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VariableSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
