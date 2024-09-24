import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from './auth.service';
import { NgForm } from '@angular/forms';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent implements OnInit {

  isLogin: boolean = true;
  username: string = "";
  password: string = "";
  email: string = "";

  constructor(private route: ActivatedRoute, private router: Router, private _service: AuthService) { }

  onSubmit(form: NgForm) {
    const userData = {
      username: form.value.username,
      password: form.value.password,
      ...(this.isLogin ? {} : { email: form.value.email })
    };

    if (this.isLogin) {
      this._service.login(userData).subscribe(
        (response:any) => {
          localStorage.setItem('token', response['access_token'])
          localStorage.setItem('id', response['id'])
          this.router.navigate(['/chat'])
        },
        error => {
          console.error('Login error', error);
        }
      );
    } else {
      this._service.signUP(userData).subscribe(
        response => {
          this.router.navigate(['/login'])
          this.isLogin = true
          console.log('Signup success!', response);
        },
        error => {
          console.error('Signup error', error);
        }
      );
    }
  }

  ngOnInit(): void {
    this.route.url.subscribe(url => {
      this.isLogin = this.router.url.includes('login');
    });
  }

  toggle() {
    this.isLogin = !this.isLogin
  }
}
