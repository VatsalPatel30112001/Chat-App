import { Component, Input, Output, OnInit, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.css']
})
export class AlertComponent implements OnInit {
  @Input() message: string = '';
  @Input() type: 'success' | 'error' | 'info' = 'info'; // Define alert types
  @Input() isVisible: boolean = false; // Control visibility
  @Output() hideAlert = new EventEmitter<any>();

  constructor() {}

  ngOnInit(): void { }

  close() {
    this.isVisible = false;
    this.hideAlert.emit('closed')
  }
}
