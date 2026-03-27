import { Injectable, inject, signal } from '@angular/core';
import { ToolModel } from '../../domain/tool/models/tool.model';
import { ToolHttpRepository } from '../../infrastructure/http/tool.http.repository';
import { UUID7 as uuid7 } from 'uuid7-typed';

@Injectable({
  providedIn: 'root',
})
export class ToolService {
  private toolRepository = inject(ToolHttpRepository);

  currentTool = signal<ToolModel | null>(null);

  getTool(toolUuid: uuid7) {
    console.log('\nbuscando tool pelo repository: ' + toolUuid + '\n');
    return this.toolRepository.getTool(toolUuid);
  }

  setCurrentTool(tool: ToolModel) {
    this.currentTool.set(tool);
  }
}
