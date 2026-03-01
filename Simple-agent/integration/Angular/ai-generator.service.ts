import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GenerationRequest {
    language: string;
    framework: string;
    task: string;
    context?: string;
    temperature?: number;
}

export interface GenerationResponse {
    code: string;
    language: string;
    framework: string;
    task: string;
    timestamp: string;
}

@Injectable({
    providedIn: 'root'
})
export class AiGeneratorService {
    // Point to the .NET Core API proxy or directly to the Python API
    private apiUrl = 'http://localhost:5000/generate';

    constructor(private http: HttpClient) { }

    generateCode(request: GenerationRequest): Observable<GenerationResponse> {
        return this.http.post<GenerationResponse>(this.apiUrl, request);
    }
}
