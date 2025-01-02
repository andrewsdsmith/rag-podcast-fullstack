import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ServerSentEventMessage } from '@app/models/server-sent-event-message';
import { QuestionRequest } from '@models/question-request';

@Injectable({
  providedIn: 'root',
})
export class StreamService {
  constructor() {}

  connectToServerSentEvents(
    url: string,
    questionRequest: QuestionRequest
  ): Observable<string> {
    return new Observable<string>((observer) => {
      const queryParams = new URLSearchParams(
        questionRequest.question
      ).toString();
      const fullUrl = `${url}?question=${queryParams}`;
      const eventSource = new EventSource(fullUrl);

      eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          observer.complete();
          eventSource.close();
          return;
        }

        const data = JSON.parse(event.data) as ServerSentEventMessage;

        const messageContent = data.message.replace(/\n/g, '<br>');
        observer.next(messageContent);
      };

      eventSource.onerror = (error) => {
        const data = JSON.parse(
          (error as MessageEvent).data
        ) as ServerSentEventMessage;
        observer.error(data);

        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    });
  }
}
