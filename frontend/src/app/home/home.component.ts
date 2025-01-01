import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { StreamService } from '@services/stream.service';
import { Subscription } from 'rxjs';
import { ClickOutsideDirective } from '@directives/click-outside.directive';
import { MarkdownModule } from 'ngx-markdown';
import { ExampleQuestion } from '@models/example-question';
import { QuestionRequest } from '@models/question-request';
import { environment } from '@environments/environment';
import { ServerSentEventMessage } from '@app/models/server-sent-event-message';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, ClickOutsideDirective, MarkdownModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.sass',
})
export class HomeComponent {
  userQuestion = '';
  answer = signal('');
  isLoading = signal(false);
  error = signal(false);
  errorMessage = signal('');
  apiUrl = environment.apiUrl;
  showPopup = true;
  showTechStackTooltip = false;
  eventSourceSubscription: Subscription | null = null;
  showTooltip = false;

  // Dynamic example questions
  exampleQuestions: ExampleQuestion[] = [
    {
      emoji: '🍎',
      text: 'Why is fiber important and how much should I eat?',
    },
    {
      emoji: '🌱',
      text: 'What are the benefits of a plant-based diet?',
    },
    {
      emoji: '🦠',
      text: 'Why is the gut microbiome so important?',
    },
    {
      emoji: '🏃',
      text: "How do I know if I'm getting enough exercise?",
    },
    {
      emoji: '🍔',
      text: 'How bad are ulta-processed foods for our health?',
    },
    {
      emoji: '🍬',
      text: 'Are there risks associated with eating a lot of sugar?',
    },
  ];

  constructor(private streamService: StreamService) {}

  submitQuestion() {
    if (!this.userQuestion.trim()) return;

    this.resetState();

    const url = `${this.apiUrl}/generator`;
    const body = { question: this.userQuestion } as QuestionRequest;
    this.eventSourceSubscription = this.streamService
      .connectToServerSentEvents(url, body)
      .subscribe({
        next: (data: string) => {
          this.error.set(false);
          this.answer.update((current) => current + data);
        },
        complete: () => {
          this.isLoading.set(false);
        },
        error: (err) => {
          const event = err as ServerSentEventMessage;
          this.isLoading.set(false);
          this.error.set(true);
          this.errorMessage.set(event.message);
        },
      });
  }

  resetState() {
    if (this.eventSourceSubscription) {
      this.eventSourceSubscription.unsubscribe();
    }
    this.answer.set('');
    this.isLoading.set(true);
    this.error.set(false);
    this.errorMessage.set('');
  }

  retrySubmit() {
    this.submitQuestion();
  }

  populateAndSubmit(question: string) {
    this.userQuestion = question;
    this.submitQuestion();
  }

  closePopup() {
    this.showPopup = false;
  }

  toggleTechStackTooltip() {
    this.showTechStackTooltip = !this.showTechStackTooltip;
  }
}
