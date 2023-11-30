import { Component, OnInit } from '@angular/core';
import { AuthService } from './service/auth.service';
import jwt_decode from 'jwt-decode';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { faHashtag } from '@fortawesome/free-solid-svg-icons';
import { SharedDataService } from './service/SharedDataService';

@Component({
  selector: 'userprofile',
  templateUrl: './userprofile.component.html',
  styleUrls: ['./userprofile.component.css']
})

export class UserProfileComponent implements OnInit {

  profileJson: any;

    
  constructor(public http: HttpClient,
              public authService: AuthService,
              public route: ActivatedRoute,
              private sharedDataService: SharedDataService
              ) {}


  admin: boolean = false;
  favourite_ID: any;
  password: any

  favourites: any[] = [];
  userdetails: any;

  userId: any;
  userName: any;
  userEmail: any;
  userIsAdmin: boolean = false;
  decodedToken: any;
  activeTab: string | any;
  faHashtag = faHashtag;


favouriteTransactions: any[] = [];
favouriteAddresses: any[] = [];
favouriteBlocks: any[] = [];



updateQuery(event: MouseEvent){
  // Prevent the default hyperlink action
  event.preventDefault(); 

    // Get the hyperlink text
    const target = event.target as HTMLAnchorElement;
    const newQuery = target.textContent;
    const dataField = target.getAttribute("data-field");

    // Retrieve the stored object
    const storedData: string | null = localStorage.getItem('requestData');
    const requestData: any = storedData ? JSON.parse(storedData) : null;
    requestData.field = null;
    requestData.page = 1;

    if (requestData) {

      requestData.query = newQuery;
      if (dataField == "block"){

        //Update "querytype" field
        requestData.querytype = "block";
      }
      else if (dataField == "address"){
      //Update "querytype" field
        requestData.querytype = "address";
      }

      // Store the updated object back to localStorage
      localStorage.setItem('requestData', JSON.stringify(requestData));
      this.sharedDataService.updateRequestData(requestData);
      this.sharedDataService.fetchSearchResults(requestData);
    }

}



  ngOnInit() {
    this.userdetails = this.getDecodedToken();
    this.fetchAllFavourites();
    this.favourite_ID = this.http.get('http://localhost:5000/api/v1.0/userprofile/' + this.userdetails["_id"] + '/favourites/' + this.favourite_ID);


  }


  
  deleteUser(asset:any){
    if (confirm('Are you sure you want to delete this account?')) {
    let str = String(asset);
    console.log("http://localhost:5000/api/v1.0/user-manager/" + str);
    localStorage.removeItem('token');
    return this.http.delete("http://localhost:5000/api/v1.0/user-manager/" + str).subscribe();
    
    

   }
   else {
     return null;
   }
  }
  
  getDecodedToken() {
    const token = localStorage.getItem('token');
    if (token) {
      const tokenPayload = jwt_decode(token);
      return tokenPayload;
    } else {
      return null;
    }
  }
  
  token = localStorage.getItem('token');


  setActiveTab(tab: string) {
    this.activeTab = tab;
  }

  


  deleteFavourite(favourite_id: string) {
    this.http.delete('http://localhost:5000/api/v1.0/userprofile/' + this.userdetails["_id"] + '/favourites/' + favourite_id)
      .subscribe((data: any) => {
        console.log(data);
        // Refresh the favourites list after deletion
       this.fetchAllFavourites();
        
      });
  }
  
  getFavouriteDetails(favourite_id: string) {
    this.http.get('http://localhost:5000/api/v1.0/userprofile/' + this.userdetails["_id"] + '/favourites/' + favourite_id)
      .subscribe((data: any) => {
        console.log(data);
      });
      return this.favourite_ID;
  }


  fetchAllFavourites() {
    this.http.get<any[]>('http://localhost:5000/api/v1.0/userprofile/' + this.userdetails["_id"] + '/favourites/all')
      .subscribe((data: any[]) => {
        console.log("Raw data:", data);
        this.favouriteAddresses = data.filter(favourite => {
          console.log("Address filter:", favourite.favouriteType === 'address', favourite);
          return favourite.favouriteType === 'address';
        });
        this.favouriteBlocks = data.filter(favourite => {
          console.log("Block filter:", favourite.favouriteType === 'block', favourite);
          return favourite.favouriteType === 'block';
        });  
        console.log(this.favouriteAddresses);
        console.log(this.favouriteBlocks);
        console.log(this.favouriteTransactions);
      });
  }


  clickforlog() {
    console.log(this.favourites);
  }

}
