import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class StreamService {
  constructor() {}

  connectToServerSentEvents(url: string): Observable<string> {
    return new Observable<string>((observer) => {
      const eventSource = new EventSource(url);

      eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          observer.complete();
          eventSource.close();
        } else {
          observer.next(event.data);
        }
      };

      eventSource.onerror = (error) => {
        observer.error(error);
        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    });
  }
}
