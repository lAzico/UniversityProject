import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { SharedDataService } from '../service/SharedDataService';
import { faUser} from '@fortawesome/free-solid-svg-icons';
import { faFileLines } from '@fortawesome/free-solid-svg-icons';
import {faMoneyBill} from '@fortawesome/free-solid-svg-icons';
import {faCube} from '@fortawesome/free-solid-svg-icons';
import {faCheckCircle} from '@fortawesome/free-solid-svg-icons';
import {faTimesCircle} from '@fortawesome/free-solid-svg-icons';
import { faAddressCard} from '@fortawesome/free-solid-svg-icons';
import { faOilCan } from '@fortawesome/free-solid-svg-icons';
import { faHashtag } from '@fortawesome/free-solid-svg-icons';
import { faCoins } from '@fortawesome/free-solid-svg-icons';
import { faClock } from '@fortawesome/free-solid-svg-icons';
import { faSignOut } from '@fortawesome/free-solid-svg-icons';
import { faSignIn } from '@fortawesome/free-solid-svg-icons';
import { faGasPump } from '@fortawesome/free-solid-svg-icons';
import { faMoneyCheckDollar } from '@fortawesome/free-solid-svg-icons';
import {NgxPaginationModule} from 'ngx-pagination';
import { faStar } from '@fortawesome/free-solid-svg-icons';



@Component({
  selector: 'app-block',
  templateUrl: './block.component.html',
  styleUrls: ['./block.component.css']
})
export class BlockComponent implements OnInit {

    currentBlock: string | null = null;
    blockData: any;
    pageSize: number = 10;
    query: string = '';
    balance: any;
    request: any;
    paramMapSubscription!: Subscription;
    queryParamsSubscription!: Subscription;
    requestDataSubscription!: Subscription;
    blockDataSubscription!: Subscription;
    currentPage: number;
    network: any;
    faFileLines = faFileLines;
    faMoneyBill = faMoneyBill;
    faCube = faCube;
    faCheckCircle = faCheckCircle;
    faTimesCircle = faTimesCircle;
    faAddressCard = faAddressCard;
    faOilCan = faOilCan;
    faHashtag = faHashtag;
    faCoins = faCoins;
    faUser = faUser;
    faClock = faClock;
    faSignOut = faSignOut;
    faSignIn = faSignIn;
    faGasPump = faGasPump;
    faMoneyCheckDollar = faMoneyCheckDollar;
    faStar = faStar;
    activeTab: string | any = 'block';
    page: number = 1;

  
    constructor(private route: ActivatedRoute, private sharedDataService: SharedDataService) {
      const storedData: string | null = localStorage.getItem('requestData');
      const requestData: any = storedData ? JSON.parse(storedData) : null;
      this.currentPage = requestData && requestData.page ? requestData.page : 1;
      this.network = requestData && requestData.network ? requestData.network : 'Unknown';  }
  
    ngOnInit(): void {
      this.route.params.subscribe(params => {
        this.currentBlock = params['blockid'];
      });
  
      this.blockDataSubscription = this.sharedDataService.currentBlockData.subscribe((data: any) => {
        if (localStorage.getItem('blockData')) {
          this.blockData = JSON.parse(localStorage.getItem('blockData') || '{}');
        } else {
          this.blockData = data;
          localStorage.setItem('blockData', JSON.stringify(data));
        }
      });
    }
  
    ngOnDestroy() {
      if (this.paramMapSubscription) {
        this.paramMapSubscription.unsubscribe();
      }
      if (this.blockDataSubscription) {
        this.blockDataSubscription.unsubscribe();
      }
    }
  
  

    addFavourite() {
    
      const storedData: string | null = localStorage.getItem('blockData');
      const transactionData: any = storedData ? JSON.parse(storedData) : null;
      transactionData.favouriteType = "block";
  
      this.sharedDataService.postFavouriteData(transactionData);
    }
    setActiveTab(tab: string) {
      this.activeTab = tab;
    }
  
    updateQuery(event: MouseEvent) {
      // Prevent the default hyperlink action
      event.preventDefault();
    
      if (this.paramMapSubscription) {
        this.paramMapSubscription.unsubscribe();
      }
    
      // Get the hyperlink text and data-field attribute
      const target = event.target as HTMLAnchorElement;
      const newQuery = target.textContent;
      const field = target.getAttribute('data-field');
    
      // Retrieve the stored object
      const storedData: string | null = localStorage.getItem('requestData');
      const requestData: any = storedData ? JSON.parse(storedData) : null;
    
      if (requestData) {
        // Update the "query" field
        requestData.query = newQuery;
    
        // Update the "querytype" field based on the clicked field
        if (field === 'address') {
          requestData.querytype = 'address';
        } else if (field === 'transaction') {
          requestData.querytype = 'transaction';
        } else if (field === 'block') {
          requestData.querytype = 'block';
        }
    
        // Store the updated object back to localStorage
        localStorage.setItem('requestData', JSON.stringify(requestData));
        this.sharedDataService.updateRequestData(requestData);
        this.sharedDataService.fetchSearchResults(requestData);
      }
    }
  
    nextPage() {
  
        this.currentPage++;
        // Update the page field
        const storedData: string | null = localStorage.getItem('requestData');
        const requestData: any = storedData ? JSON.parse(storedData) : null;
        if (requestData) {
          requestData.page = this.currentPage;
          localStorage.setItem('requestData', JSON.stringify(requestData));
          this.sharedDataService.updateRequestData(requestData);
          this.sharedDataService.fetchSearchResults(requestData);
        } 
        console.log(this.currentBlock)
      }
  
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        // Update the page field
        const storedData: string | null = localStorage.getItem('requestData');
        const requestData: any = storedData ? JSON.parse(storedData) : null;
        if (requestData) {
          requestData.page = this.currentPage;
          localStorage.setItem('requestData', JSON.stringify(requestData));
          this.sharedDataService.updateRequestData(requestData);
          this.sharedDataService.fetchSearchResults(requestData);
        }
      }
    }
}