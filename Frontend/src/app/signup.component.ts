import { Component, OnInit } from '@angular/core';
import { AuthService } from './service/auth.service';
import { Router } from '@angular/router';
import { FormBuilder, Validators } from '@angular/forms';


@Component({
  selector: 'usersignup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
  
})

export class SignUpComponent implements OnInit {


  password: any;
  isPasswordVisible = false;
constructor(public service: AuthService,
            private formBuilder: FormBuilder,
            private router: Router){}


SignUpForm: any;

ngOnInit() {
    
  this.SignUpForm = this.formBuilder.group({
    username: ['', Validators.required],
    name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required]

  });

}


togglePasswordVisibility() {
  const passwordField = document.getElementById('password') as HTMLInputElement;
  passwordField.type = this.isPasswordVisible ? 'password' : 'text';
  this.isPasswordVisible = !this.isPasswordVisible;
}
signUp(){
  
  const payload = { username: this.SignUpForm.get('username')?.value, password: this.SignUpForm.get('password')?.value,
                    email: this.SignUpForm.get('email')?.value, name: this.SignUpForm.get('name')?.value};
                    console.log(JSON.stringify(payload))
  this.service.Signup(payload).subscribe(result => {
       if (result != null) {
  
       //redirect to home page
        }});
  

        

}

  



}

