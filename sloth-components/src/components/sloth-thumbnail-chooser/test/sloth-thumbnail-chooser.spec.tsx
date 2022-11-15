import { newSpecPage } from '@stencil/core/testing';
import { SlothThumbnailChooser } from '../sloth-thumbnail-chooser';

describe('sloth-thumbnail-chooser', () => {
  it('renders', async () => {
    const page = await newSpecPage({
      components: [SlothThumbnailChooser],
      html: `<sloth-thumbnail-chooser></sloth-thumbnail-chooser>`,
    });
    expect(page.root).toEqualHtml(`
      <sloth-thumbnail-chooser>
        <mock:shadow-root>
          <slot></slot>
        </mock:shadow-root>
      </sloth-thumbnail-chooser>
    `);
  });
});
