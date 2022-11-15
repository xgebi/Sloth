import { newE2EPage } from '@stencil/core/testing';

describe('side-bar', () => {
  it('renders', async () => {
    const page = await newE2EPage();
    await page.setContent('<side-bar></side-bar>');

    const element = await page.find('side-bar');
    expect(element).toHaveClass('hydrated');
  });
});
