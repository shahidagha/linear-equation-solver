import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class EquationApiService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  saveSystem(payload: any) {
    return this.http.post(`${this.apiUrl}/save-system`, payload);
  }

  solveSystem(payload: any) {
    return this.http.post(`${this.apiUrl}/solve-system`, payload);
  }

  getSystems() {
    return this.http.get(`${this.apiUrl}/systems`);
  }

}