import { newE2EPage } from '@stencil/core/testing';

describe('sloth-editor', () => {
  it('renders', async () => {
    const page = await newE2EPage();
    await page.setContent('<sloth-editor></sloth-editor>');

    const element = await page.find('sloth-editor');
    expect(element).toHaveClass('hydrated');
  });
});
