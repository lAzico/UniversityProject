import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { JwtModule } from '@auth0/angular-jwt';
import { AuthService } from './service/auth.service';
import { Base64 } from 'js-base64';


@Component({
  selector: 'login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']})

export class LoginComponent implements OnInit {

  messageclass='';
  message='';
  userID: any;
  editdata: any;
  responsedata: any;
  userdata: any;
  loginresult: any;
  username: any;
  password: any;
  isPasswordVisible = false;



  constructor(private service: AuthService, private Router: Router) { 
    localStorage.clear();
  }
  Login = new FormGroup({
    username: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required])
  });

  ngOnInit(): void {
  }





  togglePasswordVisibility() {
    const passwordField = document.getElementById('password') as HTMLInputElement;
    passwordField.type = this.isPasswordVisible ? 'password' : 'text';
    this.isPasswordVisible = !this.isPasswordVisible;
  }
  login() {

    const payload = { username: this.Login.get('username')?.value, password: this.Login.get('password')?.value};

    this.service.Login(payload).subscribe(result => {
      if (result != null) {
        this.responsedata = result;
        localStorage.setItem('token', this.responsedata.token);
        //redirect to home page
        this.Router.navigateByUrl('/userprofile');
    }});
    

  

    
  
  }
}






