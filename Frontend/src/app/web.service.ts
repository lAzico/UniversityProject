import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { JsonPipe } from '@angular/common';
import { AuthService } from './service/auth.service';

@Injectable()
export class WebService {

    private assetID: any;
    token: any;
    private userID: any;


    assets_list: any;

    constructor(public http: HttpClient,
                public auth: AuthService) {}



    


    
    deleteUser(id: any){
        return this.http.delete('http://localhost:5000/api/v1.0/user-manager/' + id );
    }


    deleteAsset(id: any){
        return this.http.delete('http://localhost:5000/api/v1.0/assets/' + id );
    }

    deleteReview(id: any, id2: any, token: any){
        token = localStorage.getItem('id');
        return this.http.delete('http://localhost:5000/api/v1.0/assets/' + id + 'reviews/' + id2, token );
    }

    updateAsset(asset: any){
        return this.http.put('http://localhost:5000/api/v1.0/assets/' + 
                                   asset, this.http);
        }
    

    getReview(assetID: any, reviewID: any) {
        return this.http.get('http://localhost:5000/api/v1.0/assets/' + assetID + '/reviews/' + reviewID);
        }

    getUsers(page: number){
        return this.http.get('http://localhost:5000/api/v1.0/user-manager?pn=' + page);
    }
    
    getUser(id: any){
        return this.http.get('http://localhost:5000/api/v1.0/user-profile/' + id );
    }

    getAssets(page: number) {
    return this.http.get('http://localhost:5000/api/v1.0/assets?pn=' + page);
    }

    getAsset(id: any) {
        this.assetID = id;
        return this.http.get('http://localhost:5000/api/v1.0/assets/' + this.assetID);
    }


    getNotes(id: number) {
        return this.http.get('http://localhost:5000/api/v1.0/user-manager/' + id  + '/notes');
        }

    getReviewCount(id: number) {
        return this.http.get('http://localhost:5000/api/v1.0/assets/' + id + '/reviews/count').subscribe(
        (data: any) =>
        JSON.parse(data)
        
        );
    }


    


    getUserID(){
        this.token = localStorage.getItem('token');
        return this.http.post('http://localhost:5000/api/v1.0/userprofile', this.token).subscribe(
            (data: any) => {
            this.userID = data['_id'];
            console.log(this.userID);
            }
        );
    }



    postNote(note: any){
        let postData = new FormData();
        postData.append("name", note.name)
        postData.append("note", note.note)
        let userID = JSON.stringify(localStorage.getItem('token'));
        postData.append("user_id", this.userID)

        let today = new Date();
        let todayDate = today.getFullYear() + "-" +
                            today.getMonth() + "-" +
                            today.getDate();
        postData.append("date", todayDate);
    
        return this.http.post('http://localhost:5000/api/v1.0/user-manager/' + 
                                   this.userID + '/notes', postData);
        }



    getReviews(id: number) {
        return this.http.get('http://localhost:5000/api/v1.0/assets/' + id + '/reviews');
        }

    postReview(review: any){
        let postData = new FormData();
        let userID = this.getUserID();
        if (userID != null){
            postData.append("user_id", JSON.stringify(localStorage.getItem('_id')));
            console.log(JSON.stringify(localStorage.getItem('_id')));
        }

        postData.append("name", review.name)
        postData.append("review", review.review)
        postData.append("rating", review.rating)


        let today = new Date();
        let todayDate = today.getFullYear() + "-" +
                        today.getMonth() + "-" +
                        today.getDate();
        postData.append("date", todayDate);
        return this.http.post('http://localhost:5000/api/v1.0/assets/' + 
                               this.assetID + '/reviews', postData);

                               
    }

    postAsset(asset: any){
        let postData = new FormData();
       

        postData.append("Name", asset.Name)
        postData.append("Price", asset.Image)
        postData.append("Profile", asset.Type)
        postData.append("Symbol", asset.Symbol)
        postData.append("availableSupply", asset.availableSupply)

        return this.http.post('http://localhost:5000/api/v1.0/assets', postData);

                               
    }

 }
