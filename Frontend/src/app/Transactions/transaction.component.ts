import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SharedDataService } from '../service/SharedDataService';
import { Subscription } from 'rxjs';
import { faFileLines } from '@fortawesome/free-solid-svg-icons';
import {faMoneyBill} from '@fortawesome/free-solid-svg-icons';
import {faCube} from '@fortawesome/free-solid-svg-icons';
import {faCheckCircle} from '@fortawesome/free-solid-svg-icons';
import {faTimesCircle} from '@fortawesome/free-solid-svg-icons';
import { faAddressCard} from '@fortawesome/free-solid-svg-icons';
import { faHashtag } from '@fortawesome/free-solid-svg-icons';
import { faCoins } from '@fortawesome/free-solid-svg-icons';
import { faClock } from '@fortawesome/free-solid-svg-icons';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';
import {faMoneyCheckDollar} from '@fortawesome/free-solid-svg-icons';
import { faSignIn } from '@fortawesome/free-solid-svg-icons';
import { faSignOut } from '@fortawesome/free-solid-svg-icons';
import { faGasPump } from '@fortawesome/free-solid-svg-icons';
import { faShareNodes } from '@fortawesome/free-solid-svg-icons';
import { faCircleNodes } from '@fortawesome/free-solid-svg-icons';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';
import { faStar } from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-transaction',
  templateUrl: './transaction.component.html',
  styleUrls: ['./transaction.component.css']
})
export class TransactionComponent implements OnInit, OnDestroy {
  transactionData: any;
  paramMapSubscription!: Subscription;
  queryParamsSubscription!: Subscription;
  transactionDataSubscription!: Subscription;
  currentTransaction: string | null = null;
  faFileLines = faFileLines;
  faMoneyBill = faMoneyBill;
  faCube = faCube;
  faCheckCircle = faCheckCircle;
  faTimesCircle = faTimesCircle;
  faAddressCard = faAddressCard;
  faHashtag = faHashtag;
  faCoins = faCoins;
  faClock = faClock;
  faArrowRight = faArrowRight;
  faArrowLeft = faArrowLeft;
  faMoneyCheckDollar = faMoneyCheckDollar;
  faSignIn = faSignIn;
  faSignOut = faSignOut;
  faGasPump = faGasPump;
  faShareNodes = faShareNodes;
  faCircleNodes = faCircleNodes;
  faStar = faStar;

  activeTab: string | any = 'transaction';
  network: any;

  
  
  constructor(private route: ActivatedRoute, private sharedDataService: SharedDataService, private http: HttpClient) { 
    const storedData: string | null = localStorage.getItem('requestData');
    const requestData: any = storedData ? JSON.parse(storedData) : null;
    this.network = requestData && requestData.network ? requestData.network : 'Unknown';  }



  ngOnInit(): void {


    this.route.paramMap.subscribe(params => {
      this.currentTransaction = params.get('txid');
    });

    this.transactionDataSubscription = this.sharedDataService.currentTransactionData.subscribe((data: any) => {
      if (localStorage.getItem('transactionData')) {
        this.transactionData = JSON.parse(localStorage.getItem('transactionData') || '{}');
      } else {
        this.transactionData = data;
        localStorage.setItem('transactionData', JSON.stringify(data));
      }
    });
  }

  addFavourite() {
    
    const storedData: string | null = localStorage.getItem('transactionData');
    const transactionData: any = storedData ? JSON.parse(storedData) : null;
    transactionData.favouriteType = "transaction";

    this.sharedDataService.postFavouriteData(transactionData);
  }

  isArray(obj: any): boolean {
    return Array.isArray(obj);
  }


  ngOnDestroy() {
    if (this.paramMapSubscription) {
      this.paramMapSubscription.unsubscribe();
    }
    if (this.queryParamsSubscription) {
      this.queryParamsSubscription.unsubscribe();
    }
    if (this.transactionDataSubscription) {
      this.transactionDataSubscription.unsubscribe();
    }
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
  }
  updateQuery(event: MouseEvent){
    // Prevent the default hyperlink action
    event.preventDefault(); 
    if (this.paramMapSubscription) {
      this.paramMapSubscription.unsubscribe();
    }
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
}