import { HttpClient } from '@angular/common/http';
import { Injectable, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import jwt_decode from 'jwt-decode';


@Injectable({
  providedIn: 'root'
})
export class AuthService implements OnInit{


  constructor(private http: HttpClient,
              private router: Router) { }

  apiurl = 'http://localhost:5000/api/v1.0/login';
  apiurl4 = 'http://localhost:5000/api/v1.0/signup';
  profileJson: any;
  admin: any;
  id: any;
  username: any;
  token = localStorage.getItem('token');

ngOnInit(){
  this.admin = this.getDecodedToken()['admin'];
}
getDecodedToken(): any {
  const token = localStorage.getItem('token');
  if (token) {
    const tokenPayload = jwt_decode(token);
    return tokenPayload;
  } else {
    return null;
  }
}

Login(payload: any) {
  return this.http.post(this.apiurl, payload)
}

isAdmin(){
  if (this.admin == true){
    return true;
  }
  else {
    return false;
  }
}

Signup(payload: any){
  return this.http.post(this.apiurl4, payload)
}

isAuthenticated(){

  if (localStorage.getItem('token') != null){
    return true;
  }
  else {
    return false;
  }
  }

  logout(){
    localStorage.removeItem('token');
    this.router.navigate(['']);
  }
  isLoggedOut(){
    if (localStorage.getItem('token') == null){
      return true;
    }
    else {
      return false;
    }
  }
}