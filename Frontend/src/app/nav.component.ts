import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { AuthService } from './service/auth.service';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import jwt_decode from 'jwt-decode';

@Component({
  selector: 'navigation',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit{
  id: any;
    constructor(public authService: AuthService,
                public router: Router,
                public http: HttpClient,
                private cdr: ChangeDetectorRef){}
  
  localstorage: any;
  userdetails: any;
  profileJson: any;
  isAdminValue: boolean = false;
  token: any;
  request: any;

  admin: boolean = false;
  ngOnInit() {

    this.token = localStorage.getItem('token');
    this.userdetails = this.getDecodedToken();
    


  }

  ngAfterViewInit() {
    this.cdr.detectChanges();
  }

  getDecodedToken() {
    this.token = localStorage.getItem('token');
    if (this.token) {
      const tokenPayload = jwt_decode(this.token);
      return tokenPayload;
    } else {
      return null;
    }
  }

  clearRequestData(){
    localStorage.removeItem('requestData');
    this.router.navigate(['/']);
  }
  
isAdmin(){
  this.userdetails = this.getDecodedToken();
 
  if (this.userdetails && this.userdetails.admin != null) {
  if (this.userdetails.admin == true){
    return true;
  }
  else {
    return false;
  }
  

}
else {
  return false;
}
}
}