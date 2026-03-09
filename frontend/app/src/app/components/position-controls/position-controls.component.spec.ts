import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PositionControlsComponent } from './position-controls.component';

describe('PositionControlsComponent', () => {
  let component: PositionControlsComponent;
  let fixture: ComponentFixture<PositionControlsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PositionControlsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PositionControlsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
