import { newSpecPage } from '@stencil/core/testing';
import { SlothButton } from '../sloth-button';

describe('sloth-button', () => {
  it('renders', async () => {
    const page = await newSpecPage({
      components: [SlothButton],
      html: `<sloth-button></sloth-button>`,
    });
    expect(page.root).toEqualHtml(`
      <sloth-button>
        <mock:shadow-root>
          <slot></slot>
        </mock:shadow-root>
      </sloth-button>
    `);
  });
});
