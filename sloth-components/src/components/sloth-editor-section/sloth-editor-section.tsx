import {Component, Event, EventEmitter, h, Prop} from '@stencil/core';
import {SectionTypes} from "../../enums/section-types";
import {EditorSectionActions} from "../../enums/editor-section-actions";

@Component({
  tag: 'sloth-editor-section',
  styleUrl: 'sloth-editor-section.css',
  shadow: true,
})
export class SlothEditorSection {
  @Prop() type: string;

  @Prop() sectionId: string;

  @Prop() contentTargetLanguage: string;

  @Prop() contentOriginalLanguage: string;

  @Event() action: EventEmitter<{ action: EditorSectionActions, id: string }>;

  render() {
    return (
      <section class={`sloth-editor ${this.contentOriginalLanguage?.length > 0 ? 'sloth-editor--translation-mode' : 'sloth-editor--original-mode'}`}>
        {this.contentOriginalLanguage?.length > 0 && <div>{this.contentOriginalLanguage}</div>}
        <textarea>{this.contentTargetLanguage}</textarea>
        <select>
          <option value="">--Please choose an option--</option>
          <option value={SectionTypes.Text} selected={this.type === SectionTypes.Text}>{SectionTypes.Text}</option>
          <option value={SectionTypes.Form} selected={this.type === SectionTypes.Form}>{SectionTypes.Form}</option>
        </select>
        <div class="sloth-editor__action-buttons">
          <div>
            <button onClick={this.moveUp.bind(this)}>🔼</button>
            <button onClick={this.moveDown.bind(this)}>🔽</button>
          </div>
          <button onClick={this.deleteSection.bind(this)}>🗑️</button>
        </div>
      </section>
    );
  }

  moveUp() {
    this.action.emit({ action: EditorSectionActions.Up, id: this.sectionId })
  }

  moveDown() {
    this.action.emit({ action: EditorSectionActions.Down, id: this.sectionId })
  }

  deleteSection() {
    this.action.emit({ action: EditorSectionActions.Delete, id: this.sectionId })
  }
}
