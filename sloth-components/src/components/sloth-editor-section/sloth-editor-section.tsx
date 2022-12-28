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

  @Prop() position: number;

  @Prop() contentTargetLanguage: string;

  @Prop() contentOriginalLanguage: string;

  @Event() sectionUpdated: EventEmitter<{ action: EditorSectionActions, uuid: string, data?: string }>;

  @Prop() mediaList: string;

  @State() type_;

  textarea = null;

  input = null;

  connectedCallback() {
    this.type_ = this.type;
  }

  render() {
    const localContent = this.contentTargetLanguage;
    return (
      <section class={`sloth-editor-section ${this.contentOriginalLanguage?.length > 0 ? 'sloth-editor-section--translation-mode' : 'sloth-editor-section--original-mode'} ${this.position <= 1 ? 'sloth-editor-section--top-sections' : ''}`}>
        {this.contentOriginalLanguage?.length > 0 &&
          <strong class="sloth-editor-section__original-column-name">Original language</strong>}
        <strong class="sloth-editor-section__target-column-name">Target language</strong>
        {this.position === 0 && <strong class="sloth-editor-section__headline">Excerpt</strong>}
        {this.position === 1 && <strong class="sloth-editor-section__headline">Content</strong>}
        {this.contentOriginalLanguage?.length > 0 && <div class="sloth-editor-section__original">{this.contentOriginalLanguage}</div>}
        {this.type_ === SectionTypes.Text && <textarea ref={(el) => {this.textarea = el}} onBlur={this.contentChanged.bind(this)} class="sloth-editor-section__target">{localContent}</textarea>}
        {this.type_ === SectionTypes.Form && <input ref={(el) => {this.input = el}} onBlur={this.contentChanged.bind(this)} value={this.contentTargetLanguage} />}
        {this.type_ === SectionTypes.Image && <sloth-media-picker />}
        <select onChange={this.typeChanged.bind(this)}>
          <option value="">--Please choose an option--</option>
          <option value={SectionTypes.Text} selected={this.type === SectionTypes.Text}>{SectionTypes.Text}</option>
          <option value={SectionTypes.Form} selected={this.type === SectionTypes.Form}>{SectionTypes.Form}</option>
          <option value={SectionTypes.Image} selected={this.type === SectionTypes.Image}>{SectionTypes.Image}</option>
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
    this.sectionUpdated.emit({ action: EditorSectionActions.Up, uuid: this.sectionId })
  }

  moveDown() {
    this.sectionUpdated.emit({ action: EditorSectionActions.Down, uuid: this.sectionId })
  }

  deleteSection() {
    this.sectionUpdated.emit({ action: EditorSectionActions.Delete, uuid: this.sectionId })
  }

  typeChanged(e: Event) {
    this.type_ = e.target['value'];
    this.sectionUpdated.emit({ action: EditorSectionActions.TypeChanged, uuid: this.sectionId,  data: e.target['value'] })
  }

  contentChanged(e: Event) {
    this.sectionUpdated.emit({ action: EditorSectionActions.ContentChanged, uuid: this.sectionId,  data: e.target['value'] })
  }


  disconnectedCallback() {
    console.log('section unmounted')
  }

  componentDidUpdate() {
    this.type_ = this.type;
    if (this.textarea) {
      this.textarea.value = this.contentTargetLanguage
    }
    if (this.input) {
      this.input.value = this.contentTargetLanguage
    }
  }
}
