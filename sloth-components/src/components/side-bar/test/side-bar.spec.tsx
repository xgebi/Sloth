import { newSpecPage } from '@stencil/core/testing';
import { SideBar } from '../side-bar';

describe('side-bar', () => {
  it('renders', async () => {
    const page = await newSpecPage({
      components: [SideBar],
      html: `<side-bar></side-bar>`,
    });
    expect(page.root).toEqualHtml(`
      <side-bar>
        <mock:shadow-root>
          <slot></slot>
        </mock:shadow-root>
      </side-bar>
    `);
  });
});
