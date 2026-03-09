import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EquationBuilderComponent } from './equation-builder.component';

describe('EquationBuilderComponent', () => {
  let component: EquationBuilderComponent;
  let fixture: ComponentFixture<EquationBuilderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EquationBuilderComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EquationBuilderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
