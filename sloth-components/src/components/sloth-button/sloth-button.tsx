import { Component, Host, h } from '@stencil/core';

@Component({
  tag: 'sloth-button',
  styleUrl: 'sloth-button.scss',
  shadow: true,
})
export class SlothButton {

  render() {
    return (
      <Host>
        <slot></slot>
      </Host>
    );
  }

}
