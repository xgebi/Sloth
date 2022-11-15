import { newSpecPage } from '@stencil/core/testing';
import { SlothEditorSection } from '../sloth-editor-section';

describe('sloth-editor-section', () => {
  it('renders', async () => {
    const page = await newSpecPage({
      components: [SlothEditorSection],
      html: `<sloth-editor-section></sloth-editor-section>`,
    });
    expect(page.root).toEqualHtml(`
      <sloth-editor-section>
        <mock:shadow-root>
          <slot></slot>
        </mock:shadow-root>
      </sloth-editor-section>
    `);
  });
});
