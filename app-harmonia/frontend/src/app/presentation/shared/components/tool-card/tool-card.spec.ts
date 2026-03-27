import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ToolCard } from './tool-card';
import { UUID7 as uuid7 } from 'uuid7-typed';

describe('ToolCard', () => {
  let component: ToolCard;
  let fixture: ComponentFixture<ToolCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ToolCard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ToolCard);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('tool', '12345678-1234-5678-1234-567812345678' as unknown as uuid7);
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
