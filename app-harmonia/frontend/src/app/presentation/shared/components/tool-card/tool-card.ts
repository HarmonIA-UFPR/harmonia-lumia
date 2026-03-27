// tool-card.component.ts
import { Component, input, Output, EventEmitter, inject, signal, effect } from '@angular/core';
import { UUID7 as uuid7} from 'uuid7-typed';
import { ToolService } from '../../../../application/tool/tool.service';
import { ToolModel } from '../../../../domain/tool/models/tool.model';

@Component({
  selector: 'app-tool-card',
  standalone: true,
  imports: [],
  templateUrl: './tool-card.html',
  styleUrls: ['./tool-card.css']
})
export class ToolCard {
  tool = input.required<uuid7>();
  
  @Output() toolSelected = new EventEmitter<ToolModel>();

  private toolService = inject(ToolService);
  
  // Guardamos a ferramenta carregada neste signal local
  toolI = signal<ToolModel | null>(null);
  
  // Controle de estado para a UI
  clickedDesc = false;

  constructor() {
    // Reage sempre que o input 'tool' mudar
    effect(() => {
      const id = this.tool();
      if (id) {
        this.toolService.getTool(id).subscribe({
          next: (data) => {
            this.toolI.set(data);
          },
          error: (err) => {
            console.error('Erro ao buscar ferramenta no ToolCard:', err);
            this.toolI.set(null);
          }
        });
      }
    });
  }

  toggleDesc(event: Event) {
    event.stopPropagation();
    this.clickedDesc = !this.clickedDesc;
  }

  shortDesc() {
    const desc = this.toolI()?.tool_description || '';
    return desc.length > 34 ? `${desc.slice(0, 34)}...` : desc;
  }

  viewTool(): void {
    const currentTool = this.toolI();
    if (currentTool) {
      this.toolSelected.emit(currentTool);
    }
  }

  handleLinkClick(event: Event): void {
    event.stopPropagation();
  }
}
