import { Component, Host, h } from '@stencil/core';

@Component({
  tag: 'side-bar',
  styleUrl: 'side-bar.css',
  shadow: true,
})
export class SideBar {

  render() {
    return (
      <Host>
        <slot></slot>
      </Host>
    );
  }

}
