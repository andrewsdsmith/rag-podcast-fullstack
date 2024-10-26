import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { StreamService } from '../services/stream.service';
import { ConfigService } from '../services/config.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';
import { Subscription } from 'rxjs';
import { ClickOutsideDirective } from '../directives/click-outside.directive';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, ClickOutsideDirective],
  templateUrl: './home.component.html',
  styleUrl: './home.component.sass',
})
export class HomeComponent {
  userQuestion = '';
  answer = signal(''); // Raw markdown
  renderedAnswer = signal<SafeHtml>(''); // Rendered HTML
  isLoading = signal(false);
  error = signal(false); // Tracks if an error occurred
  errorMessage = signal(''); // Stores the error message
  apiUrl = this.configService.getConfig().apiUrl;
  showPopup = true; // Initially, the popup is shown
  showTechStackTooltip = false;
  eventSourceSubscription: Subscription | null = null;

  constructor(
    private configService: ConfigService,
    private streamService: StreamService,
    private sanitizer: DomSanitizer
  ) {}

  submitQuestion() {
    if (!this.userQuestion.trim()) return;

    this.resetState();

    const url = `${this.apiUrl}/generator/question?text=${encodeURIComponent(
      this.userQuestion
    )}`;
    this.eventSourceSubscription = this.streamService
      .connectToServerSentEvents(url)
      .subscribe({
        next: async (data: string) => {
          this.error.set(false); // Reset error state on successful data

          this.answer.update((current) => current + data);

          // Parse the markdown and update the rendered HTML
          const updatedMarkdown = this.answer();
          const html = await marked(updatedMarkdown);
          this.renderedAnswer.update(() =>
            this.sanitizer.bypassSecurityTrustHtml(html)
          );
        },
        complete: () => {
          this.isLoading.set(false);
        },
        error: (err) => {
          console.error('Error in stream:', err);
          this.isLoading.set(false);
          this.error.set(true); // Set error state
          this.errorMessage.set(this.getErrorMessage(err));
        },
      });
  }

  resetState() {
    if (this.eventSourceSubscription) {
      this.eventSourceSubscription.unsubscribe();
    }
    this.answer.set('');
    this.renderedAnswer.set(''); // Reset the rendered answer
    this.isLoading.set(true);
    this.error.set(false); // Reset error state
    this.errorMessage.set(''); // Clear any previous error messages
  }

  retrySubmit() {
    this.submitQuestion(); // Re-attempt to submit the question
  }

  getErrorMessage(err: any): string {
    if (err instanceof Event && err.type === 'error') {
      return 'Network error. Please check your internet connection and try again.';
    }
    return 'An unexpected error occurred. Please try again later.';
  }

  populateAndSubmit(question: string) {
    this.userQuestion = question;
    this.submitQuestion();
  }

  closePopup() {
    this.showPopup = false; // Close the popup when user acknowledges the warning
  }

  toggleTechStackTooltip() {
    this.showTechStackTooltip = !this.showTechStackTooltip;
  }
}
