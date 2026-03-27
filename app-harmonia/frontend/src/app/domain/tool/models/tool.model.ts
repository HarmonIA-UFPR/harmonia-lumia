import { UUID7 as uuid7 } from 'uuid7-typed';
export interface ToolModel {
    tool_uuidv7: uuid7;
    tool_name: string;
    tool_description: string;
    tool_data_prog: boolean;
    tool_official_link: string | null;
    tool_repository_link: string | null;
    tool_documentation_link: string | null;
    tool_complexity: number;
}
