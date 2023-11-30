import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import jwtDecode from 'jwt-decode';
import { EventEmitter } from '@angular/core';
@Injectable({
  providedIn: 'root',
})
export class SharedDataService {
  private transactionData = new BehaviorSubject<any>({});
  currentTransactionData = this.transactionData.asObservable();

  private blockData = new BehaviorSubject<any>({});
  currentBlockData = this.blockData.asObservable();

  private addressData = new BehaviorSubject<any>({});
  currentAddressData = this.addressData.asObservable();

  public requestData = new BehaviorSubject<any>({});
  currentRequestData = this.requestData.asObservable();

  errorEvent: EventEmitter<string> = new EventEmitter<string>();
  



  constructor(private router: Router, private http: HttpClient) {}

  handleAPIResponse(data: any, query: string, queryType: string) {

    const queryParams: any = {};
  
    
    if (queryType === 'address') {
      if(data[1] == "transactions"){
        let addressdata = JSON.parse(localStorage.getItem('addressData') || '{}');
        addressdata["Transactions"] = data[0];
        let modifiedData = JSON.stringify(addressdata);
        localStorage.setItem('addressData', modifiedData);
        this.updateAddressData(modifiedData)
        this.router.navigate([`/address/${query}`]), { queryParams };
      }
      else if (data[1] == "internal_transactions"){
        let addressdata = JSON.parse(localStorage.getItem('addressData') || '{}');
        addressdata["Internal Transactions"] = data[0];
        let modifiedData = JSON.stringify(addressdata);
        localStorage.setItem('addressData', modifiedData);
        this.updateAddressData(modifiedData)
        this.router.navigate([`/address/${query}`]), { queryParams };
      }
      else if (data[1] == "erc20_transactions"){
        let addressdata = JSON.parse(localStorage.getItem('addressData') || '{}');
        addressdata["ERC-20 Transactions"] = data[0];
        let modifiedData = JSON.stringify(addressdata);
        localStorage.setItem('addressData', modifiedData);
        this.updateAddressData(modifiedData)
        this.router.navigate([`/address/${query}`]), { queryParams };
      }
      else{
      localStorage.removeItem('addressData');
      this.updateAddressData(data);
      this.router.navigate([`/address/${query}`]), { queryParams };
      }
    } else if (queryType === 'transaction') {
      localStorage.removeItem('transactionData');
      this.updateTransactionData(data);
      queryParams.txid = data.txid;
      this.router.navigate([`/transaction/${query}`]), { queryParams };
    } else if (queryType === 'block') {
      localStorage.removeItem('blockData');
      this.updateBlockData(data);
      queryParams.blockNumber = data.blockNumber;
      this.router.navigate([`/block/${query}`], { queryParams });
    } else if(queryType === 'text'){
      queryParams.text = data.text;
      this.router.navigate(['/text'], { queryParams });
    } else
      console.error('Unknown query type');
    }

  updateRequestData(data: any) {
    this.requestData.next(data);
  }

  updateAddressData(data: any) {
    this.addressData.next(data);
  }

  updateBlockData(data: any) {
    this.blockData.next(data);
  }

  updateTransactionData(data: any) {
    this.transactionData.next(data);
  }

    fetchSearchResults(requestData: any) {
      if (!requestData.field) { 
         requestData.field = null
      }
      if (!requestData.offset || requestData.offset < 0){
          requestData.offset = 10
      }
      if (!requestData.page){
          requestData.page = 1
      }

      console.log(requestData)
      console.log("Executing fetchSearchResults")
      this.http.post('http://localhost:5000/api/v1.0/Search', requestData)
        .subscribe((data: any) => {
          console.log(data);
          if (data.error) {
           this.errorEvent.emit(data.error);
            return;
          }

          this.handleAPIResponse(data, requestData.query, requestData.querytype);
        });
    }

    fetchSearchResultsPages(requestData: any) {

      if (requestData.field) { 
        requestData.field = null
     }
     if (requestData.offset || requestData.offset < 0){
         requestData.offset = 10
     }
     if (requestData.page){
         requestData.page = 1
     }

      console.log(requestData)
      console.log("Executing fetchSearchResults")
      this.http.post('http://localhost:5000/api/v1.0/Search', requestData)
        .subscribe((data: any) => {
          console.log(data);
          this.handleAPIResponse(data, requestData.query, requestData.querytype);
        });
    }

    postFavouriteData(requestData: any) {

      

      const token = localStorage.getItem('token') || '';
      if (!token) {
        this.errorEvent.emit('Please login to add to favourites');
        return;
      }
      const decoded: any = jwtDecode(token);
      const id = decoded._id;

      console.log(decoded)
      console.log("Executing postFavouriteData")
      this.http.post('http://localhost:5000/api/v1.0/userprofile/' + id + '/favourites', requestData)
        .subscribe((data: any) => {
          console.log(data);
        });
    }

  }
