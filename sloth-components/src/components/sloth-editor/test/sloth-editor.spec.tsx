import { newSpecPage } from '@stencil/core/testing';
import { SlothEditor } from '../sloth-editor';

describe('sloth-editor', () => {
  it('renders', async () => {
    const page = await newSpecPage({
      components: [SlothEditor],
      html: `<sloth-editor></sloth-editor>`,
    });
    expect(page.root).toEqualHtml(`
      <sloth-editor>
        <mock:shadow-root>
          <slot></slot>
        </mock:shadow-root>
      </sloth-editor>
    `);
  });
});
