import { Component } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { WebService } from './web.service';
import { Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Router } from '@angular/router';
import { SharedDataService } from './service/SharedDataService';
import { takeUntil } from 'rxjs/operators';
import { Subject, Subscription, interval } from 'rxjs';
import { NONE_TYPE } from '@angular/compiler';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import { MatSnackBar } from '@angular/material/snack-bar';


export interface LoginResponse{
    token: string;
}

@Component({
 selector: 'home',
 templateUrl: './home.component.html',
 styleUrls: ['./home.component.css']
})
export class HomeComponent {
    

    email = '';
    password = '';
    searchBar: any;
    searchValue: any;
    networks:any = [];
    networksapp: any = [];
    networksMap: any = {};
    queryMap: any = {};
    reversedNetworksMap: any = {};
    reversedQueryMap: any = {};
    queryType: any;
    selectedQuery: any;
    currentPage = 1;
    HomePageTransactions: any = [];
    allData: any = [];
    allDataString: any = '';
    private ngUnsubscribe = new Subject<void>();
    paramMapSubscription!: Subscription;
    faSearch = faSearch;
    errorMessage: string | null = null;

    constructor(
                private formBuilder: FormBuilder,
                private webService: WebService,
                private http: HttpClient,
                private router: Router,
                private sharedDataService: SharedDataService,
                private snackBar: MatSnackBar){

                }



                ngOnInit() {
                  this.refreshData();
                  interval(20000)
                    .pipe(takeUntil(this.ngUnsubscribe))
                    .subscribe(() => {
                      this.refreshData();
                    });
                
                    this.sharedDataService.errorEvent.subscribe((errorMsg: string) => {
                      this.showErrorSnackBar(errorMsg);
                    });

                    this.searchBar = this.formBuilder.group({
                        querytype: ['', Validators.required],
                        network: ['', Validators.required],
                        query: ['', Validators.required]
                    });

                    this.networksapp = [
                    "avalanche",
                    "fantom",
                    "polygon",
                    "binance",
                    "ethereum",
                    "bitcoin", 
                    "bitcoin-cash",  
                    "litecoin", 
                    "dogecoin", 
                    // "dash", 
                    "ripple", 
                    "groestlcoin", 
                    // "stellar", 
                    // "monero", 
                    // "cardano", 
                    "zcash", 
                    // "mixin", 
                    // "tezos",
                    // "eos",
                    "ecash"]
                    this.networks =   [
                    "Avalanche",
                    "Fantom",
                    "Polygon",
                    "Binance Smart Chain",
                    "Bitcoin",
                    "Bitcoin Cash",
                    "Ethereum",
                    "Litecoin",
                    "Dogecoin",
                    "Ripple",
                    // "Dash",
                    "Groestlcoin",
                    // "Stellar",
                    // "Monero",
                    // "Cardano",
                    "Zcash",
                    // "Mixin",
                    // "Tezos",
                    // "EOS",
                    "eCash",
                ];

                this.queryType = ['address', 
                'transaction', 
                'block'];

                this.networksMap = {
                    'avalanche': 'Avalanche',
                    'fantom': 'Fantom',
                    'polygon': 'Polygon',
                    'binance': 'Binance Smart Chain',
                    'bitcoin': 'Bitcoin',
                    'bitcoin-cash': 'Bitcoin Cash',
                    'ethereum': 'Ethereum',
                    'litecoin': 'Litecoin',
                    'dogecoin': 'Dogecoin',
                    'ripple': 'Ripple',
                    // 'dash': 'Dash',
                    'groestlcoin': 'Groestlcoin',
                    // 'stellar': 'Stellar',
                    // 'monero': 'Monero',
                    // 'cardano': 'Cardano',
                    'zcash': 'Zcash',
                    // 'mixin': 'Mixin',
                    // 'tezos': 'Tezos',
                    // 'eos': 'EOS',
                    'ecash': 'eCash'
                  };
                  

                  this.queryMap = {
                    'address': 'Address',
                    'transaction': 'Transaction',
                    'block': 'Block',
                  };
                 

                 
                  for (const key in this.networksMap) {
                    this.reversedNetworksMap[this.networksMap[key]] = key;
                  }

                    for (const key in this.queryMap) {
                    this.reversedQueryMap[this.queryMap[key]] = key;
                  
                    
                }
                this.selectedQuery = 'Select query type';
    
                }

                selectedNetwork = 'Select network';
                
                
                ngOnDestroy() {
                  this.ngUnsubscribe.next();
                  this.ngUnsubscribe.complete();
                }


                showErrorSnackBar(message: string) {
                  this.snackBar.open(message, 'Close', {
                    duration: 5000,
                    panelClass: ['error-snackbar'],
                  });
                }
                refreshData(): void {
                  console.log('refreshing data');
                  this.http
                    .get('http://localhost:5000/api/v1.0/HomePage')
                    .subscribe((result) => {
                      localStorage.setItem('homeData', JSON.stringify(result));
                      this.allData = result;
                      console.log(result);
                    });
                }

                

                updateNetwork(network: string) {
                    this.selectedNetwork = this.networksMap[network];
                    this.searchBar.network = this.networksMap[this.selectedNetwork];
                    // Use the reversed network map to get the opposite value
                    const oppositeValue = this.reversedNetworksMap[this.selectedNetwork];
                    console.log(oppositeValue);
                  }

                  updateQuery(query: string) {
                    this.selectedQuery = this.queryMap[query];
                    this.searchBar.querytype = this.queryMap[this.selectedQuery];

                    // Use the reversed network map to get the opposite value
                    const oppositeValue = this.reversedQueryMap[this.selectedQuery];

                    console.log(oppositeValue);
                  }


                  updateForMouseClick(event: MouseEvent) {
                    // Prevent the default hyperlink action
                    event.preventDefault();
                  
                    if (this.paramMapSubscription) {
                      this.paramMapSubscription.unsubscribe();
                    }
                  
                    
                    // Get the hyperlink text and data-field attribute
                    const target = event.target as HTMLAnchorElement;
                    const newQuery = target.textContent;
                    const network = target.getAttribute('data-network');
                    const field = target.getAttribute('data-field');
                    const requestData: any = {};


                    target.setAttribute('data-network', this.searchBar.get('network').value);
                    if (field === 'address') {
                      requestData.querytype = 'address';
                      requestData.query = newQuery;
                      requestData.field = null;
                      requestData.offset = null;
                    } else if (field === 'transaction') {
                      requestData.querytype = 'transaction';
                      requestData.query = newQuery;
                    }
                      else if (field === 'block') {
                      requestData.querytype = 'block';   
                      requestData.query = newQuery;                 
                    }


                    requestData['network'] = network?.toLowerCase() || NONE_TYPE;
                    // Retrieve the stored object

                    const storedData: string | null = localStorage.getItem('requestData');
                  
                  
                      // Store the updated object back to localStorage
                      localStorage.setItem('requestData', JSON.stringify(requestData));
                      this.sharedDataService.updateRequestData(requestData);
                      this.sharedDataService.fetchSearchResults(requestData);
                    }
                  

                SearchTextEntered(searchValue: string){

                    this.searchBar.query = searchValue; 
                    console.log(this.searchBar.query);

                }


                prevPage() {
                  if (this.currentPage > 1) {
                    this.currentPage -= 1;
                  }
                }
              
                nextPage() {
                  this.currentPage += 1;
                }

                onSubmit() {
                  if (this.searchBar.valid) {
                    const requestData = this.searchBar.value;
                    requestData.page = this.currentPage;
                    localStorage.removeItem('addressData');
                    localStorage.setItem('requestData', JSON.stringify(requestData));
                    this.sharedDataService.updateRequestData(requestData);
                    this.sharedDataService.fetchSearchResults(requestData);
                    this.errorMessage = null;
                  } else {
                    this.errorMessage = 'Enter all required fields';
                  }
                }

              }
