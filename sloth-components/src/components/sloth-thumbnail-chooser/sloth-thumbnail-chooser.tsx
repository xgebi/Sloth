import { Component, Host, h } from '@stencil/core';

@Component({
  tag: 'sloth-thumbnail-chooser',
  styleUrl: 'sloth-thumbnail-chooser.css',
  shadow: true,
})
export class SlothThumbnailChooser {

  render() {
    return (
      <Host>
        <slot></slot>
      </Host>
    );
  }

}
