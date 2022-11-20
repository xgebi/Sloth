import { newE2EPage } from '@stencil/core/testing';

describe('sloth-button', () => {
  it('renders', async () => {
    const page = await newE2EPage();
    await page.setContent('<sloth-button></sloth-button>');

    const element = await page.find('sloth-button');
    expect(element).toHaveClass('hydrated');
  });
});
