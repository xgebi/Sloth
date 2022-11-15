import { newE2EPage } from '@stencil/core/testing';

describe('sloth-editor-section', () => {
  it('renders', async () => {
    const page = await newE2EPage();
    await page.setContent('<sloth-editor-section></sloth-editor-section>');

    const element = await page.find('sloth-editor-section');
    expect(element).toHaveClass('hydrated');
  });
});
