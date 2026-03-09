import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EquationPreviewComponent } from './equation-preview.component';

describe('EquationPreviewComponent', () => {
  let component: EquationPreviewComponent;
  let fixture: ComponentFixture<EquationPreviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EquationPreviewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EquationPreviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
