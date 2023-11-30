import { Component } from '@angular/core';
import { WebService } from './web.service';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, Validators } from '@angular/forms';



@Component({
 selector: 'notes',
 templateUrl: './notes.component.html',
 styleUrls: ['./notes.component.css']
 
})
export class NotesComponent { 

    notesForm: any;
    users_list: any = [];
    notes: any = [];
    
    constructor(public webService: WebService,
                private route: ActivatedRoute,
                private formBuilder: FormBuilder,
                ) {}
    
                ngOnInit() {
                    this.notesForm = this.formBuilder.group({
                        name: ['', Validators.required],
                        note: ['', Validators.required],
                    });
            
                this.users_list = this.webService.getUser(this.route.snapshot.params['id']);
                this.notes = this.webService.getNotes(this.route.snapshot.params['id']);
            
                     
                }
                onSubmit() {
                    
                    this.webService.postNote(this.notesForm.value)
                    .subscribe( (response: any) => {
                        this.notesForm.reset();
                        this.notes = this.webService.getNotes(this.route.snapshot.params['id'])
                    })
                    this.notesForm.reset();
                }
            
                isInvalid(control: any){
                    return this.notesForm.controls[control].invalid &&
                           this.notesForm.controls[control].touched;
                }
            
                isUnTouched(){
                    return this.notesForm.controls.name.pristine ||
                           this.notesForm.controls.note.pristine;
                }
                
                isIncomplete(){
                    return this.isInvalid('name') ||
                           this.isInvalid('note') ||
                           this.isUnTouched();
                }
            }
            