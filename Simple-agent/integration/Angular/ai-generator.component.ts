import { Component } from '@angular/core';
import { AiGeneratorService, GenerationRequest, GenerationResponse } from './ai-generator.service';

@Component({
    selector: 'app-ai-generator',
    template: `
    <div class="ai-container">
      <h2>AI Code Generator</h2>
      
      <div class="input-group">
        <label>Language:</label>
        <select [(ngModel)]="request.language">
          <option value="csharp">C#</option>
          <option value="typescript">TypeScript</option>
          <option value="sql">SQL</option>
        </select>
      </div>

      <div class="input-group">
        <label>Framework:</label>
        <select [(ngModel)]="request.framework">
          <option value="dotnet8">.NET 8</option>
          <option value="angular">Angular</option>
          <option value="mssql">MS SQL</option>
        </select>
      </div>

      <div class="input-group">
        <label>Describe your task:</label>
        <textarea [(ngModel)]="request.task" placeholder="e.g. Create a user login component"></textarea>
      </div>

      <button (click)="generate()" [disabled]="loading">
        {{ loading ? 'Generating...' : 'Generate Code' }}
      </button>

      <div *ngIf="generatedCode" class="output-group">
        <h3>Generated Code:</h3>
        <pre><code>{{ generatedCode }}</code></pre>
      </div>

      <div *ngIf="error" class="error-message">
        {{ error }}
      </div>
    </div>
  `,
    styles: [`
    .ai-container { padding: 20px; border: 1px solid #ddd; border-radius: 8px; max-width: 600px; }
    .input-group { margin-bottom: 15px; }
    label { display: block; margin-bottom: 5px; font-weight: bold; }
    select, textarea { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc; }
    textarea { height: 100px; }
    button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
    button:disabled { background-color: #ccc; }
    pre { background-color: #f4f4f4; padding: 15px; border-radius: 4px; overflow-x: auto; margin-top: 10px; }
    .error-message { color: red; margin-top: 10px; }
  `]
})
export class AiGeneratorComponent {
    request: GenerationRequest = {
        language: 'csharp',
        framework: 'dotnet8',
        task: ''
    };

    generatedCode: string = '';
    loading: boolean = false;
    error: string | null = null;

    constructor(private aiService: AiGeneratorService) { }

    generate() {
        if (!this.request.task) {
            this.error = "Please enter a task description.";
            return;
        }

        this.loading = true;
        this.error = null;
        this.generatedCode = '';

        this.aiService.generateCode(this.request).subscribe({
            next: (res: GenerationResponse) => {
                this.generatedCode = res.code;
                this.loading = false;
            },
            error: (err) => {
                this.error = "Error generating code. Please ensure the AI engine is running.";
                this.loading = false;
                console.error(err);
            }
        });
    }
}
