import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Config } from '../models/config';

@Injectable({
  providedIn: 'root',
})
export class ConfigService {
  private config!: Config;

  constructor(private http: HttpClient) {}

  async loadConfig(): Promise<void> {
    this.config = await firstValueFrom(this.http.get<Config>('config.json'));
  }

  getConfig(): Config {
    return this.config;
  }
}
