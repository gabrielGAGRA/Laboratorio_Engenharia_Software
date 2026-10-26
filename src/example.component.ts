import { ChangeDetectionStrategy, Component, signal } from '@angular/core';

@Component({
  selector: 'app-example',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './example.component.html',
})
export class ExampleComponent {
  protected readonly count = signal<number>(0);
}
