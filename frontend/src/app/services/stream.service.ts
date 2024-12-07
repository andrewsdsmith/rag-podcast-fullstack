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
    body: QuestionRequest
  ): Observable<string> {
    return new Observable<string>((observer) => {
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify(body),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();

          function push() {
            reader
              ?.read()
              .then(({ done, value }) => {
                if (done) {
                  observer.complete();
                  return;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                lines.forEach((line) => {
                  if (line.startsWith('data: ')) {
                    const data = JSON.parse(
                      line.slice(6)
                    ) as ServerSentEventMessage;

                    if (data.message === '[DONE]') {
                      observer.complete();
                    } else {
                      const messageContent = data.message.replace(
                        /\n/g,
                        '<br>'
                      );
                      observer.next(messageContent);
                    }
                  }
                });

                push();
              })
              .catch((error) => {
                observer.error(error);
              });
          }

          push();

          return () => {
            reader?.cancel();
          };
        })
        .catch((error) => {
          observer.error(error);
        });
    });
  }
}
