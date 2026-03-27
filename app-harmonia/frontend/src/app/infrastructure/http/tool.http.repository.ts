import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { ToolModel } from '../../domain/tool/models/tool.model';
import { UUID7 as uuid7 } from 'uuid7-typed';
import { environment } from '../../../environments/environment';
// Opcionalmente, pode implementar uma interface que estaria em domain/tool/repositories/tool.repository.ts

interface ToolApiResponse {
  tool_name: string;
  tool_description: string;
  tool_data_prog: boolean;
  tool_official_link: string | null;
  tool_repository_link: string | null;
  tool_documentation_link: string | null;
  tool_complexity: number;
  tool_uuidv7: uuid7;
}

@Injectable({ providedIn: 'root' })
export class ToolHttpRepository {
  private http = inject(HttpClient);
  private readonly API_URL = environment.apiUrl;

  getTool(toolUuid: uuid7): Observable<ToolModel> {
    return  this.http.get<ToolApiResponse>(`${this.API_URL}/tools/${toolUuid}`).pipe(
                map((apiData: ToolApiResponse) => {
                    // Aqui você faz o "match" (De / Para)
                  const domainModel: ToolModel = {
                    // Garantindo a tipagem do uuid
                    tool_uuidv7: apiData.tool_uuidv7 as uuid7,
                    tool_name: apiData.tool_name,
                    tool_description: apiData.tool_description,
                    tool_data_prog: apiData.tool_data_prog,
                    tool_official_link: apiData.tool_official_link,
                    tool_repository_link: apiData.tool_repository_link,
                    tool_documentation_link: apiData.tool_documentation_link,
                    tool_complexity: apiData.tool_complexity
                  };
                  return domainModel;
                })
              );
  }
}
