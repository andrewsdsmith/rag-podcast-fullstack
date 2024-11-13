import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { SSEEventMessage } from '@models/sse-event';

@Injectable({
  providedIn: 'root',
})
export class StreamService {
  constructor() {}

  connectToServerSentEvents(url: string): Observable<string> {
    return new Observable<string>((observer) => {
      const eventSource = new EventSource(url);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data) as SSEEventMessage;

        if (data.message === '[DONE]') {
          observer.complete();
          eventSource.close();
        } else {
          // Find newline characters and replace them with <br> tags
          const messageContent = data.message.replace(/\n/g, '<br>');
          observer.next(messageContent);
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
