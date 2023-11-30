import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, Validators, Form } from '@angular/forms';
import { AuthService } from './service/auth.service';


@Component({
  selector: 'edituser',
  templateUrl: './edituser.component.html',
  
})
export class EditUserComponent implements OnInit {


    constructor(private route: ActivatedRoute,
               private http: HttpClient,
               public formBuilder: FormBuilder,
               public authService: AuthService
                ) {}
                 
  
user_id: any;
request: any;
user: any;
requestForm: any;
edit_form: any;
userdata: any;
ngOnInit(){

    this.edit_form = this.formBuilder.group({
        name: ['', Validators.required],
        username: ['', Validators.required],
        email: ['', Validators.required],
        password: ['', Validators.required],
        admin: [null]

});

    this.user_id = this.route.snapshot.paramMap.get('id');
    this.userdata = this.http.get('http://localhost:5000/api/v1.0/userprofile/' + this.route.snapshot.paramMap.get('id')).subscribe(data => {
      this.user = data;
})}

  






updateUser(payload: any) {
    let edit_form = payload.value
    this.request = this.http.put('http://localhost:5000//api/v1.0/userprofile/' + this.user_id, edit_form).subscribe(data => {  
    console.log(data);
});
}


onSubmit(){

this.updateUser(this.edit_form)
this.edit_form.reset();


}
}