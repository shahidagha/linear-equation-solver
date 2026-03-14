import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SolverResponse } from '../models/solver-response.model';

const API_BASE = 'http://127.0.0.1:8000';
const API_V1 = `${API_BASE}/v1`;

@Injectable({
  providedIn: 'root'
})
export class EquationApiService {
  private apiUrl = API_V1;

  constructor(private http: HttpClient) {}

  saveSystem(payload: any): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/save-system`, payload);
  }

  solveSystem(payload: any): Observable<SolverResponse> {
    return this.http.post<SolverResponse>(`${this.apiUrl}/solve-system`, payload);
  }

  getSystems(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/systems`);
  }

  deleteSystem(systemId: number): Observable<{ status: string }> {
    return this.http.delete<{ status: string }>(`${this.apiUrl}/system/${systemId}`);
  }
}

