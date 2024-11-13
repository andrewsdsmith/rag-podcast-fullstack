import { MarkedOptions, MarkedRenderer } from 'ngx-markdown';

export function markedOptionsFactory(): MarkedOptions {
  const renderer = new MarkedRenderer();

  // Override the link renderer to add target="_blank"
  renderer.link = (href: string, title: string, text: string) => {
    const titleAttr = title ? `title="${title}"` : '';
    return `<a href="${href}" ${titleAttr} target="_blank">${text}</a>`;
  };

  return {
    renderer,
  };
}
