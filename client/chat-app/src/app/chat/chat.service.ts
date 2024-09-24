import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environment/enviroment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  baseURL = environment.baseUrl + '/api'

  constructor(private http: HttpClient) {}

  getPersonalChats(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseURL}/all-users-and-groups`);
  }

  getChatHistory(recipient_id:number, group_id:number) {
    let params = new HttpParams
    params = params.set('recipient_id', recipient_id)
    params = params.set('group_id', group_id)
    return this.http.get(this.baseURL+'/message-history', {params})
  }

  sendMessage(recipient_id: any, group_id: any, file: any, message: string): Observable<any> {
    const formData = new FormData();
    formData.append('recipient_id', recipient_id);
    formData.append('group_id', group_id);
    formData.append('file', file);
    formData.append('content', message);
    return this.http.post(`${this.baseURL}/send-message`, formData);
  }

  joinGroup(group_id:any, user_id:any) {
    return this.http.post(`${this.baseURL}/join-group`, {
      'group_id': group_id,
      'user_id':user_id
    })
  }
  
  createGroup(group_name: string, user_id: any) {
    return this.http.post(`${this.baseURL}/create-group`, {
      'group_name': group_name,
      'member_ids':[user_id]
    })
  }

  downloadFile(file_path: string) {
    return this.http.post(`${this.baseURL}/download-file`, {
      'file_path':file_path
    }, { responseType: 'blob' })
  }
}
