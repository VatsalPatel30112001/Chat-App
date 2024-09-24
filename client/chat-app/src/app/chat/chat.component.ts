import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { ChatService } from './chat.service';
import { SocketService } from '../socket.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  personalChats: any[] = [];
  groupChats: any[] = [];
  selectedChat: any;
  newMessage: string = "";
  groupName: string = "";
  userName: string = "";
  newGroupName: string = "";
  messages: any = []
  userId: any = 0;
  isFileSelected: boolean = false;
  selectedFile: any;
  alertMessage: any = ""
  alertType: any = ""
  alertVisible: any = false
  join = false;
  createNewGroup = false;
  @ViewChild('fileInput') fileInput: any;

  constructor(private chatService: ChatService, private socketService: SocketService, private router: Router) {}

  ngOnInit() {
    this.socketService.onMessage().subscribe((message: any) => {
      if (message.hasOwnProperty("info")) {
        this.alertMessage = message['info']
        this.alertType = 'info'
        this.alertVisible = true
      } else if (message.hasOwnProperty("new_user")) {
        this.personalChats.push(message['new_user'])
        this.alertMessage = `${message['new_user']['user_name']} registered`
        this.alertType = 'info'
        this.alertVisible = true
      } else if (message.hasOwnProperty("new_group")) {
        this.groupChats.push(message['new_group'])
        this.alertMessage = `${message['created_by']} created new group ${message['new_group']['group_name']}`
        this.alertType = 'info'
        this.alertVisible = true
      }
      else {
        if (this.selectedChat && this.selectedChat.hasOwnProperty('user_id') && !message['group_id'] && this.selectedChat['user_id']==message['sender_id']) {
          this.messages.push(message)
        } else if(this.selectedChat && this.selectedChat.hasOwnProperty('group_id') && this.selectedChat['group_id']==message['group_id']) {
          this.messages.push(message)
        } else {
          if (message['group_id']) {
            let group = this.groupChats.find(item => item.group_id==message['group_id'])
            this.alertMessage = (message['is_file']) ? `${message['sender_name']} shared a file in ${group.group_name}` : `${message['sender_name']} sent message in ${group.group_name}`
          } else {
            this.alertMessage = (message['is_file']) ? `${message['sender_name']} sent you a file` : `${message['sender_name']} sent you a message`
          }
          this.alertType = 'info'
          this.alertVisible = true
        }
      }
    });
    this.loadChats();
    this.userId = localStorage.getItem('id');
  }

  closeEvent(event:string) {
    this.alertVisible = false
  }

  loadChats() {
    this.chatService.getPersonalChats().subscribe((chats: any) => {
      this.personalChats = chats['users']
      this.groupChats = chats['groups']
    });
  }

  selectChat(chat: any) {
    this.selectedChat = chat;
    if (chat.hasOwnProperty('user_id')) {
      this.userName = chat.user_name
      this.groupName = ""
    } else {
      this.groupName = chat.group_name
      this.userName = ""
    }
    let recipient_id = (chat.hasOwnProperty('user_id')) ? chat.user_id : null
    let group_id = (chat.hasOwnProperty('group_id')) ? chat.group_id : null
    if (recipient_id || (group_id && chat['is_member'] == true)) {
      this.join = false
      this.chatService.getChatHistory(recipient_id, group_id).subscribe((chats: any) => {
        this.messages = chats
      }, (error)=> console.log(error))
    } else {
      this.join = true
    }
  }

  joinGroup() {
    this.chatService.joinGroup(this.selectedChat['group_id'], this.userId).subscribe((resp: any) => {
      this.selectedChat['is_member'] = true
      this.join = false
      this.selectChat(this.selectedChat)
    })
  }

  createGroup() {
    this.chatService.createGroup(this.newGroupName, this.userId).subscribe((resp:any) => {
      this.groupChats.push(resp['new_group'])
      this.createNewGroup = false
    })
  }
  
  resetFields() {
    this.newMessage = '';
    this.selectedFile = null;
    this.isFileSelected = false;

    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }

  onFileSelected(event:any) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.isFileSelected = true;
      this.newMessage = this.selectedFile.name; 
    } else {
      this.resetFields()
    }
  }

  sendMessage() {
    if (this.newMessage.trim() || this.selectedFile) {
      const messageData = {
        text: this.newMessage.trim(),
        file: this.selectedFile,
      };
      let recipient_id = (this.selectedChat.hasOwnProperty('user_id')) ? this.selectedChat.user_id : null
      let group_id = (this.selectedChat.hasOwnProperty('group_id')) ? this.selectedChat.group_id : null

      this.chatService.sendMessage(recipient_id, group_id, this.selectedFile, this.newMessage).subscribe((resp:any) => {
        this.messages.push(resp['new_message']);
        this.newMessage = '';
        this.resetFields();
      });
    }
  }

  downloadFile(filePath: string, file_name:string): void {
    this.chatService.downloadFile(filePath).subscribe((blob: any) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');       
      a.href = url;
      a.download = file_name;          
      a.click();                                   
      window.URL.revokeObjectURL(url); 
    })
  }

  logOut() {
    localStorage.removeItem('token')
    localStorage.removeItem('id')
    this.socketService.disconnectSocket()
    this.router.navigate(['/login'])
  }
}
