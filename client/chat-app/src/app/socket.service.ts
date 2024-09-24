import { Injectable } from '@angular/core';
import { Socket } from 'socket.io-client';
import { Observable } from 'rxjs';
import { io } from 'socket.io-client';
import { environment } from 'src/environment/enviroment';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: Socket | null = null;

  constructor() {
    this.socket = io(environment.baseUrl, {
      query: {
          id: localStorage.getItem('id') 
      }
    }); 
  }

  public disconnectSocket() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null; 
    }
  }

  public onMessage() {
    return new Observable(observer => {
      if (this.socket) { 
        this.socket.on('send_message', (data) => {
          observer.next(data);
        });
      }
    });
  }
}
