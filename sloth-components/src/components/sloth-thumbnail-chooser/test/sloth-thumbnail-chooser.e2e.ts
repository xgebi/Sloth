import { newE2EPage } from '@stencil/core/testing';

describe('sloth-thumbnail-chooser', () => {
  it('renders', async () => {
    const page = await newE2EPage();
    await page.setContent('<sloth-thumbnail-chooser></sloth-thumbnail-chooser>');

    const element = await page.find('sloth-thumbnail-chooser');
    expect(element).toHaveClass('hydrated');
  });
});
