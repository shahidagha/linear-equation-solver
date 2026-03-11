import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SolverResponse } from '../models/solver-response.model';

@Injectable({
  providedIn: 'root'
})
export class EquationApiService {
  private apiUrl = 'http://127.0.0.1:8000';

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

