import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppComponent } from './app.component';
import { WebService } from './web.service';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { HomeComponent } from './home.component';
import { ReactiveFormsModule } from '@angular/forms';
import { NavComponent } from './nav.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MaterialModule } from './material.module';
import { UserManagerComponent } from './user-manager.component';
import { NotesComponent } from './notes.component';
import { AgGridModule } from 'ag-grid-angular';
import { PaginatorOverview } from './paginator.component';
import { UserProfileComponent } from './userprofile.component';
import { LoginComponent } from './login.component';
import { SignUpComponent } from './signup.component';
import { EditUserComponent } from './edituser.component';
import { AddressComponent } from './Addresses/address.component';
import { TransactionComponent } from './Transactions/transaction.component';
import { BlockComponent } from './Blocks/block.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgxPaginationModule } from 'ngx-pagination';
import { TutorialComponent } from './Tutorials/tutorial.component';
import { StatsComponent } from './stats/stats.component';




var routes: any = [

  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'user-manager',
    component: UserManagerComponent
  },
  {
    path: 'user-manager/:id',
    component: NotesComponent
  },
  {
    path: 'userprofile',
    component: UserProfileComponent
  },
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'signup',
    component: SignUpComponent
  },
  {
    path: 'edituser/:id',
    component: EditUserComponent
  },
  {
    path: 'address/:query',
    component: AddressComponent
  },
    { path: 'transaction/:txid',
     component: TransactionComponent 
    },
  {
    path: 'block/:blockid',
    component: BlockComponent
  },
  {
    path: 'tutorials',
    component: TutorialComponent
  },
  { path: 'stats',
    component: StatsComponent
  }
];


@NgModule({
  declarations: [
    AppComponent, HomeComponent, 
    NavComponent, UserProfileComponent,
    UserManagerComponent, NotesComponent, PaginatorOverview, LoginComponent,
    SignUpComponent, EditUserComponent,
    AddressComponent, TransactionComponent, BlockComponent, TutorialComponent,
    StatsComponent
    
  ],
  imports: [
    BrowserModule, HttpClientModule,
    RouterModule.forRoot(routes), ReactiveFormsModule,
    FormsModule,
    AgGridModule,
    BrowserAnimationsModule, MaterialModule,
    FontAwesomeModule, NgxPaginationModule
    
  ],
  providers: [WebService],
  bootstrap: [AppComponent]
})
export class AppModule { }
