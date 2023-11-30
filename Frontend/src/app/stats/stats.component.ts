import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SharedDataService } from '../service/SharedDataService';
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
import { HttpClient } from '@angular/common/http';
import { faNetworkWired } from '@fortawesome/free-solid-svg-icons';
import { faHardHat } from '@fortawesome/free-solid-svg-icons';
import { faDollarSign } from '@fortawesome/free-solid-svg-icons';
import { faCircle } from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-stats',
  templateUrl: './stats.component.html',
  styleUrls: ['./stats.component.css']
})
export class StatsComponent implements OnInit, OnDestroy {
  //variables
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
  faNetworkWired = faNetworkWired;
  faHardHat = faHardHat;
  faDollarSign = faDollarSign;
  faCircle = faCircle;
  activeTab: string = 'stats';
  page: number = 1;

  statisticslist: any;
  

  constructor(private route: ActivatedRoute, private sharedDataService: SharedDataService, private http: HttpClient) {
    const storedData: string | null = localStorage.getItem('requestData');
    const requestData: any = storedData ? JSON.parse(storedData) : null;
  }

  ngOnInit(): void {

    this.statisticslist = this.http.get('http://localhost:5000/api/v1.0/Stats').subscribe(result => {
        this.statisticslist = result;
        localStorage.setItem('statisticslist', JSON.stringify(this.statisticslist));
        console.log(this.statisticslist);
        }
        );
  }

  ngOnDestroy() {

  }


  getBlockchainNames(): string[] {
    const allowedBlockchainNames = [
      "bitcoin",
      "bitcoin-cash",
      "ethereum",
      "litecoin",
      "dogecoin",
      "ripple",
      "groestlcoin",
      "zcash",
      "ecash",
    ];

  
    if (!this.statisticslist?.['Stats']) {
      return [];
    }
  
    const blockchainNames = Object.keys(this.statisticslist['Stats']);
    return blockchainNames.filter(name => allowedBlockchainNames.includes(name));
  }


  getHalveningNames(): string[] {
    const allowedHalveningNames = [
      "bitcoin",
      "bitcoin-cash",
      "bitcoin-sv"
    ];

  
    if (!this.statisticslist?.['Stats']) {
      return [];
    }
  
    const halveningNames = Object.keys(this.statisticslist['Stats']);
    return halveningNames.filter(name => allowedHalveningNames.includes(name));
  }

  getCapitalizedName(name: string): string {
    const nameMap: { [key: string]: string } = {
      "binance-smart-chain": "Binance Smart Chain",
      "bitcoin": "Bitcoin",
      "bitcoin-cash": "Bitcoin Cash",
      "ethereum": "Ethereum",
      "litecoin": "Litecoin",
      "bitcoin-sv": "Bitcoin SV",
      "dogecoin": "Dogecoin",
      "ripple": "Ripple",
      "groestlcoin": "Groestlcoin",
      "zcash": "Zcash",
      "ecash": "eCash",
    };
  
    return nameMap[name] || name;
  }
  abs(value: number): number {
    return Math.abs(value);
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
  }


  updateQuery(event: MouseEvent) {

  }

  nextPage(field: any) {


     
    }

  previousPage(field: any) {

  
    }
  }

