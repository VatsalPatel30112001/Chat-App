import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from './auth.service';  // Import your authentication service

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private authService: AuthService, private router: Router) {}

  canActivate(): Promise<boolean> {
    return this.authService.getUser().then(isValid => {
      if (isValid) {
        return true;
      } else {
        this.router.navigate(['/login']);
        return false;
      }
    }).catch(() => {
      this.router.navigate(['/login']);
      return false;
    });
  }
}
