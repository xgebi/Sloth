import {Component, Event, EventEmitter, h, Prop, State} from '@stencil/core';
import {SectionTypes} from "../../enums/section-types";
import {EditorSectionActions} from "../../enums/editor-section-actions";

@Component({
  tag: 'sloth-editor-section',
  styleUrl: './sloth-editor-section.scss',
  shadow: true,
})
export class SlothEditorSection {
  @Prop() type: string;

  @Prop() sectionId: string;

  @Prop() contentTargetLanguage: string;

  @Prop() contentOriginalLanguage: string;

  @Event() action: EventEmitter<{ action: EditorSectionActions, id: string }>;

  @State() type_;

  connectedCallback() {
    this.type_ = this.type;
  }

  render() {
    return (
      <section class={`sloth-editor-section ${this.contentOriginalLanguage?.length > 0 ? 'sloth-editor-section--translation-mode' : 'sloth-editor-section--original-mode'}`}>
        {this.contentOriginalLanguage?.length > 0 &&
          <strong class="sloth-editor-section__original-column-name">Original language</strong>}
        <strong class="sloth-editor-section__target-column-name">Target language</strong>
        {this.contentOriginalLanguage?.length > 0 && <div class="sloth-editor-section__original">{this.contentOriginalLanguage}</div>}
        {this.type_ === SectionTypes.Text && <textarea class="sloth-editor-section__target">{this.contentTargetLanguage}</textarea>}
        {this.type_ === SectionTypes.Form && <input value={this.contentTargetLanguage} />}
        <select onChange={this.typeChanged.bind(this)}>
          <option value="">--Please choose an option--</option>
          <option value={SectionTypes.Text} selected={this.type === SectionTypes.Text}>{SectionTypes.Text}</option>
          <option value={SectionTypes.Form} selected={this.type === SectionTypes.Form}>{SectionTypes.Form}</option>
        </select>
        <div class="sloth-editor-section__action-buttons">
          <div>
            <button class="button-icon" onClick={this.moveUp.bind(this)}>🔼</button>
            <button class="button-icon" onClick={this.moveDown.bind(this)}>🔽</button>
          </div>
          <button class="button-icon" onClick={this.deleteSection.bind(this)}>🗑️</button>
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

  typeChanged(e: Event) {
    this.type_ = e.target['value'];
  }
}
