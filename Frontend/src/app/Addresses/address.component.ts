import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SharedDataService } from '../service/SharedDataService';
import { Subscription } from 'rxjs';
import { LocalStorageCache } from '@auth0/auth0-angular';
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
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { faUser } from '@fortawesome/free-solid-svg-icons';
import { faGasPump } from '@fortawesome/free-solid-svg-icons';
import { faCalendarCheck } from '@fortawesome/free-solid-svg-icons';
import { faHandHoldingDollar } from '@fortawesome/free-solid-svg-icons';
import { faMoneyCheckDollar } from '@fortawesome/free-solid-svg-icons';
import { faSignIn } from '@fortawesome/free-solid-svg-icons';
import { faSignOut } from '@fortawesome/free-solid-svg-icons';
import {NgxPaginationModule} from 'ngx-pagination';
import { faStar } from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-address',
  templateUrl: './address.component.html',
  styleUrls: ['./address.component.css']
})
export class AddressComponent implements OnInit, OnDestroy {
  //variables
  currentAddress: string | null = null;
  addressData: any;
  pageSize: number = 10;
  query: string = '';
  balance: any;
  request: any;
  paramMapSubscription!: Subscription;
  queryParamsSubscription!: Subscription;
  requestDataSubscription!: Subscription;
  addressDataSubscription!: Subscription;
  currentPage: number;
  network: any;
  activeTab: string = 'transactions';
  transactionPage: number = 1;
  transactionPageSize: number = 10;
  internalPage: number = 1;
  internalPageSize: number = 10;
  erc20Page: number = 1;
  erc20PageSize: number = 10;
  page: number = 1;
  //fa icons
  faFileLines = faFileLines;
  faMoneyBill = faMoneyBill;
  faCube = faCube;
  faCheckCircle = faCheckCircle;
  faTimesCircle = faTimesCircle;
  faAddressCard = faAddressCard;
  faOilCan = faOilCan;
  faHashtag = faHashtag;
  faCoins = faCoins;
  faClock = faClock;
  faArrowRight = faArrowRight;
  faArrowLeft = faArrowLeft;
  faUser = faUser;
  faGasPump = faGasPump;
  faCalendarCheck = faCalendarCheck;
  faHandHoldingUsd = faHandHoldingDollar;
  faMoneyCheckDollar = faMoneyCheckDollar;
  faSignIn = faSignIn;
  faSignOut = faSignOut;
  faStar = faStar;
  

  constructor(private route: ActivatedRoute, private sharedDataService: SharedDataService) {
    const storedData: string | null = localStorage.getItem('requestData');
    const requestData: any = storedData ? JSON.parse(storedData) : null;
    this.currentPage = requestData && requestData.page ? requestData.page : 1;
    this.network = requestData && requestData.network ? requestData.network : 'Unknown';
    this.currentAddress = this.route.snapshot.paramMap.get('query');  }

  ngOnInit(): void {


    this.addressDataSubscription = this.sharedDataService.currentAddressData.subscribe((data: any) => {
      if (localStorage.getItem('addressData')) {
        this.addressData = JSON.parse(localStorage.getItem('addressData') || '{}');
      } else {
        this.addressData = data;
        localStorage.setItem('addressData', JSON.stringify(data));
      }
    });
  }

  ngOnDestroy() {
    if (this.paramMapSubscription) {
      this.paramMapSubscription.unsubscribe();
    }
    if (this.addressDataSubscription) {
      this.addressDataSubscription.unsubscribe();
    }
  }

  abs(value: number): number {
    return Math.abs(value);
  }

  addFavourite() {
    
    const storedData: string | null = localStorage.getItem('addressData');
    const transactionData: any = storedData ? JSON.parse(storedData) : null;
    transactionData.favouriteType = "address";

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
      }
        else if (field === 'block') {
        requestData.querytype = 'block';
      }
      // Store the updated object back to localStorage
      localStorage.setItem('requestData', JSON.stringify(requestData));
      this.sharedDataService.updateRequestData(requestData);
      this.sharedDataService.fetchSearchResults(requestData);
    }
  }

  nextPage(field: any) {


      if (field == 'transactions') {
        this.transactionPage++;
        this.currentPage = this.transactionPage;
        console.log(this.currentPage)
      } else if (field == 'internal_transactions') {
        this.internalPage++;
        this.currentPage = this.internalPage;
      } else if (field == 'erc20_transactions') {
        this.erc20Page++;
        this.currentPage = this.erc20Page;
      }




      // Update the page field
      const storedData: string | null = localStorage.getItem('requestData');
      const requestData: any = storedData ? JSON.parse(storedData) : null;
      if (requestData) {
        requestData.query = this.currentAddress;
        requestData.querytype = 'address';
        requestData.page = this.currentPage;
        requestData.field = this.activeTab;
        requestData.offset = 10;
        localStorage.setItem('requestData', JSON.stringify(requestData));
        this.sharedDataService.updateRequestData(requestData);
        this.sharedDataService.fetchSearchResults(requestData);
      } else {
        this.currentPage--;
      }
    }

  previousPage(field: any) {

    if (field == 'transactions') {
      this.transactionPage--;
      this.currentPage = this.transactionPage;
    } else if (field == 'internal_transactions') {
      this.internalPage--;
      this.currentPage = this.internalPage;
    } else if (field == 'erc20_transactions') {
      this.erc20Page--;
      this.currentPage = this.erc20Page;
    }

      // Update the page field
      const storedData: string | null = localStorage.getItem('requestData');
      const requestData: any = storedData ? JSON.parse(storedData) : null;
      if (requestData) {
        requestData.page = this.currentPage;
        requestData.field = this.activeTab;
        requestData.offset = 10;
        localStorage.setItem('requestData', JSON.stringify(requestData));
        this.sharedDataService.updateRequestData(requestData);
        this.sharedDataService.fetchSearchResults(requestData);
      }
    }
  }

