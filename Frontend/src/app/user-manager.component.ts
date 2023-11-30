import { Component, OnInit } from '@angular/core';
import { WebService } from './web.service';
import { ActivatedRoute } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from './service/auth.service';
import jwt_decode from 'jwt-decode';
import { Token } from '@angular/compiler';
import { Router } from '@angular/router';

@Component({
 selector: 'user-manager',
 templateUrl: './user-manager.component.html',
 styleUrls: ['./user-manager.component.css']
})
export class UserManagerComponent implements OnInit {

    users_list: any = [];
    page: number = 1;
    userdetails: any;


    constructor(private webService: WebService,
                private route: ActivatedRoute,
                private http: HttpClient,
                public authService: AuthService,
                private router: Router){}


                

                getDecodedToken() {
                    const token = localStorage.getItem('token') || '';
                    if (token) {
                        const tokenPayload = jwt_decode(token);
                        return tokenPayload;
                    } else {
                        return null;
                    }
                }

                ngOnInit() {
                    this.userdetails = this.getDecodedToken();
                    if (this.userdetails.admin == false) {
                        this.router.navigate(['/']);
                    }
                    const token = localStorage.getItem('token');
                
                    if (!token) {
                        console.log('No token found. Redirecting to login page.');
                        // Redirect to the login page or show an error message
                        this.router.navigate(['/login']);
                        return;
                    }
                
                    console.log('Token:', token);
                    const headers = new HttpHeaders().set('Authorization', 'Bearer ' + localStorage.getItem('token'));
                    this.users_list = this.http.get('http://localhost:5000/api/v1.0/user-manager', { headers });
                }
                  
                
                previousPage() { 
                    if (this.page > 1){
                        this.page = this.page - 1;
                        sessionStorage['page'] = this.page;
                        this.users_list = this.webService.getUsers(this.page);
                    }
                }
            
                nextPage() { 
                    this.page = this.page + 1;
                    sessionStorage['page'] = this.page;
                    this.users_list = this.webService.getUsers(this.page);
                }

                deleteUser(asset:any){
                    if (confirm('Are you sure you want to delete this account?')) {
                    let str = String(asset);
                    return this.http.delete("http://localhost:5000/api/v1.0/user-manager/" + str).subscribe();
                   }
                   else {
                    return null;
                   }
                }
        }
