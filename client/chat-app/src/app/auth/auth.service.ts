import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environment/enviroment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private _http: HttpClient) { }
  
  baseURL = environment.baseUrl + '/api'

 getUser(): Promise<boolean> {
  return new Promise((resolve, reject) => {
    let token = localStorage.getItem('token');
    if (token) {
      let validateURL = this.baseURL + '/validate-token';
      this._http.post(validateURL, {}).subscribe((resp: any) => {
          if (resp.hasOwnProperty('status') && resp['status'] === 'success') {
            resolve(true);
          } else {
            resolve(false);
          }
        },(error: any) => {
          reject(false);
        }
      );
    } else {
      resolve(false);
    }
  });
}

  login(data:object) {
    let loginURL = this.baseURL + '/login'
    console.log(data)
    return this._http.post(loginURL, data)
  }

  signUP(data:object) {
    let signupURL = this.baseURL + '/signup'
    return this._http.post(signupURL, data)
  }
}
