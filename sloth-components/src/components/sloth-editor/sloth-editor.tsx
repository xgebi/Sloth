import { Component, Host, h } from '@stencil/core';

@Component({
  tag: 'sloth-editor',
  styleUrl: 'sloth-editor.css',
  shadow: true,
})
export class SlothEditor {

  render() {
    return (
      <Host>
        <slot></slot>
      </Host>
    );
  }

}
