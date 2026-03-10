import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SavedSystemsComponent } from './saved-systems.component';

describe('SavedSystemsComponent', () => {
  let component: SavedSystemsComponent;
  let fixture: ComponentFixture<SavedSystemsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SavedSystemsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SavedSystemsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
